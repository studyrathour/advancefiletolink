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
        workdir="./sessions"
    )

    @client.on_message()
    async def handle_message(client, message):
        pass

    return client

async def start_bots():
    global clients

    if Config.MULTI_TOKEN:
        for i, token in enumerate(Config.MULTI_TOKEN):
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
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")

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

for route in fastapi_app.routes:
    if hasattr(route, 'path'):
        app.router.add_route(route.methods.pop(), route.path, route.endpoint)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.BIND_ADDRESS, port=Config.PORT)