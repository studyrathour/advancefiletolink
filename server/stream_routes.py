import os
import math
import time
import aiohttp
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from config import Config
import database as db
from streamer import streamer
from typing import Optional

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))
static_dir = os.path.join(BASE_DIR, "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse("File2Link Bot is running!")

@app.get("/show/{file_id}")
async def show_file(request: Request, file_id: str):
    file_data = await db.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    stream_url = f"{Config.BASE_URL()}/dl/{file_data['message_id']}/{file_id}"
    dl_url = f"{Config.BASE_URL()}/dl/{file_data['message_id']}/{file_id}?download=1"

    return templates.TemplateResponse("show.html", {
        "request": request,
        "file": file_data,
        "stream_url": stream_url,
        "dl_url": dl_url,
        "base_url": Config.BASE_URL()
    })

@app.get("/api/file/{file_id}")
async def api_file_info(file_id: str):
    file_data = await db.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "file_id": file_id,
        "file_name": file_data["file_name"],
        "file_size": file_data["file_size"],
        "downloads": file_data.get("downloads", 0),
        "stream_url": f"{Config.BASE_URL()}/dl/{file_data['message_id']}/{file_id}",
        "dl_url": f"{Config.BASE_URL()}/dl/{file_data['message_id']}/{file_id}?download=1"
    }

@app.get("/dl/{message_id}/{file_id}")
async def stream_file(
    request: Request,
    message_id: str,
    file_id: str,
    download: Optional[str] = Query(None)
):
    file_data = await db.get_file(file_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    await db.increment_downloads(file_id)

    range_header = request.headers.get("Range")
    client = request.client.host if request.client else "unknown"

    if Config.FINGERPRINT:
        await verify_fingerprint(request)

    return StreamingResponse(
        stream_content(file_data, range_header),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"{'attachment' if download else 'inline'}; filename=\"{file_data['file_name']}\"",
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_data.get("file_size", 0))
        }
    )

async def stream_content(file_data: dict, range_header: Optional[str] = None):
    from config import Config

    if not streamer or not streamer.clients:
        return

    message_id = int(file_data["message_id"])
    file_size = file_data.get("file_size", 0)

    start_offset = 0
    end_offset = file_size - 1 if file_size else 0

    if range_header:
        try:
            range_str = range_header.replace("bytes=", "")
            parts = range_str.split("-")
            start_offset = int(parts[0]) if parts[0] else 0
            end_offset = int(parts[1]) if parts[1] and parts[1] else file_size - 1
        except:
            pass

    for client in streamer.clients:
        try:
            msg = await client.get_messages(Config.BIN_CHANNEL, message_id)
            if msg:
                file = msg.document or msg.video or msg.audio or msg.voice or msg.animation
                if file:
                    file_id_str = str(file.file_id)

                    if range_header:
                        chunk_size = 1024 * 1024
                        current_offset = start_offset

                        while current_offset <= end_offset:
                            chunk_end = min(current_offset + chunk_size - 1, end_offset)
                            async for chunk in streamer.stream_file(
                                file_id_str,
                                offset=current_offset,
                                part_size=min(chunk_size, chunk_end - current_offset + 1)
                            ):
                                if chunk:
                                    yield chunk
                            current_offset += chunk_size

                            if current_offset > end_offset:
                                break
                    else:
                        async for chunk in streamer.stream_file(file_id_str):
                            if chunk:
                                yield chunk

                    return
        except Exception as e:
            print(f"Stream error with client: {e}")
            continue

    yield b""

async def verify_fingerprint(request: Request):
    fingerprint = request.headers.get("X-Fingerprint")
    if fingerprint != Config.FINGERPRINT:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.get("/admin")
async def admin_page(request: Request):
    if not Config.ADMIN_ENABLED:
        raise HTTPException(status_code=404, detail="Admin panel disabled")

    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.post("/admin/login")
async def admin_login(request: Request):
    if not Config.ADMIN_ENABLED:
        raise HTTPException(status_code=404, detail="Admin panel disabled")

    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    from config import Config
    if email == Config.ADMIN_EMAIL and password == Config.ADMIN_PASSWORD:
        return {"status": "success", "message": "Logged in!"}

    return {"status": "error", "message": "Invalid credentials"}

@app.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    if not Config.ADMIN_ENABLED:
        raise HTTPException(status_code=404, detail="Admin panel disabled")

    stats = await db.get_file_stats()
    files = await db.get_all_files(50)

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "stats": stats,
        "files": files,
        "base_url": Config.BASE_URL()
    })

@app.get("/health")
async def health_check():
    return {"status": "ok"}