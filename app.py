import asyncio
import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pyrogram import Client
from pyrogram.handlers import MessageHandler

import database as db
from config import Config
from plugins import setup_all_handlers
from server.stream_routes import app as fastapi_app
from streamer import init_streamer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

clients = []

async def create_pyrogram_client(token: str, index: int):
    client = Client(
        f"bot_{index}",
        api_id=Config.API_ID,
        api_hash=Config.API_HASH,
        bot_token=token,
        workdir="/tmp/sessions",
        in_memory=True
    )

    return client

async def start_bots():
    global clients

    logger.info(f"BOT_TOKEN: {Config.BOT_TOKEN[:20]}..." if Config.BOT_TOKEN else "BOT_TOKEN: NOT SET")
    logger.info(f"MULTI_TOKEN: {Config.get_multi_tokens()}")

    if Config.get_multi_tokens():
        for i, token in enumerate(Config.get_multi_tokens()):
            try:
                client = await create_pyrogram_client(token, i)
                await client.start()
                clients.append(client)
                logger.info(f"Bot {i+1} started successfully")
            except Exception as e:
                logger.error(f"Failed to start bot {i+1}: {e}")
    elif Config.BOT_TOKEN:
        try:
            client = await create_pyrogram_client(Config.BOT_TOKEN, 0)
            await client.start()
            clients.append(client)
            logger.info("Bot started successfully")
            logger.info(f"Bot info: {await client.get_me()}")
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            import traceback
            logger.error(traceback.format_exc())

    if clients:
        setup_all_handlers(clients[0])
        init_streamer(clients)
        logger.info("Streamer initialized")

    return clients

async def stop_bots():
    global clients
    for client in clients:
        try:
            await client.stop()
        except Exception as e:
            logger.error(f"Error stopping client: {e}")
    clients = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting File2Link Bot...")

    await db.init_db()
    logger.info("Database initialized")

    await start_bots()

    yield

    await stop_bots()
    logger.info("Bot stopped")

app = FastAPI(title="File2Link Bot", lifespan=lifespan)

app.include_router(fastapi_app.router, tags=["api"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.BIND_ADDRESS, port=Config.PORT)