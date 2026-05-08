import asyncio
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pyrogram import Client
from pyrogram.errors import FloodWait

import database as db
from config import Config
from plugins import setup_all_handlers
from server.stream_routes import app as fastapi_app
from streamer import init_streamer
from utils.logger import logger
from utils.log_helpers import log_bot_start

clients = []

async def create_pyrogram_client(token: str, index: int) -> Client:
    return Client(
        f"bot_{index}",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=token,
        workdir="/tmp/sessions",
        in_memory=True
    )

async def start_client(token: str, index: int) -> Client | None:
    """Start a single Pyrogram client, respecting any FloodWait from Telegram."""
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            client = await create_pyrogram_client(token, index)
            await client.start()
            return client
        except FloodWait as e:
            wait = e.value + 5          # add a small buffer
            logger.warning(
                f"Bot {index}: FloodWait – Telegram requires waiting {e.value}s "
                f"before login. Sleeping {wait}s (attempt {attempt}/{max_retries})..."
            )
            await asyncio.sleep(wait)   # wait the exact amount Telegram demands
        except Exception as e:
            logger.error(f"Bot {index}: Failed to start (attempt {attempt}): {e}", exc_info=True)
            if attempt < max_retries:
                await asyncio.sleep(10)
    logger.error(f"Bot {index}: Gave up after {max_retries} attempts.")
    return None

async def start_bots():
    global clients

    logger.info(f"BOT_TOKEN: {Config.BOT_TOKEN[:20]}..." if Config.BOT_TOKEN else "BOT_TOKEN: NOT SET")
    logger.info(f"MULTI_TOKEN: {Config.get_multi_tokens()}")

    tokens = Config.get_multi_tokens() or ([Config.BOT_TOKEN] if Config.BOT_TOKEN else [])

    for i, token in enumerate(tokens):
        client = await start_client(token, i)
        if client:
            clients.append(client)
            logger.info(f"Bot {i + 1} started successfully")

    if clients:
        setup_all_handlers(clients[0])
        init_streamer(clients)
        logger.info("Streamer initialized")
        try:
            me = await clients[0].get_me()
            logger.info(f"Bot info: {me}")
            await log_bot_start(clients[0], me.username or str(me.id))
        except Exception as e:
            logger.warning(f"Could not fetch bot info: {e}")
    else:
        logger.error("No bots started! Check your BOT_TOKEN and API credentials.")

    return clients

async def stop_bots():
    global clients
    for client in clients:
        try:
            await client.stop()
        except Exception as e:
            logger.error(f"Error stopping client: {e}")
    clients = []

async def _bot_startup_task():
    """Run bot startup in the background so the HTTP server starts immediately."""
    try:
        await start_bots()
    except Exception as e:
        logger.error(f"Bot startup task failed: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting File2Link Bot...")

    await db.init_db()
    logger.info("Database initialized")

    # Start bots in background — FastAPI becomes ready immediately.
    # This keeps Render's health-check happy even during a FloodWait sleep.
    asyncio.create_task(_bot_startup_task())

    yield

    await stop_bots()
    logger.info("Bot stopped")

app = FastAPI(title="File2Link Bot", lifespan=lifespan)

app.include_router(fastapi_app.router, tags=["api"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.BIND_ADDRESS, port=Config.PORT)