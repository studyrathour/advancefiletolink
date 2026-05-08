import asyncio
import os
import re
import time
import uuid
from datetime import datetime
from pyrogram import filters, Client
from pyrogram.types import Message
from config import Config
import database as db
from streamer import streamer
from utils.logger import logger
from utils.log_helpers import log_newusr, log_file_upload

FILE_TYPES = (
    filters.document | filters.video | filters.photo |
    filters.audio | filters.voice | filters.animation |
    filters.video_note
)

async def is_user_banned(user_id: int) -> bool:
    return await db.is_banned_user(user_id)

async def get_dc_id(client: Client) -> int:
    """Safely retrieve the DC ID from a Pyrogram 2.x client."""
    try:
        # In Pyrogram 2.0.x, storage.dc_id is a plain integer property
        dc = client.storage.dc_id
        if callable(dc):
            import inspect
            if inspect.iscoroutinefunction(dc):
                return await dc()
            return dc()
        return int(dc)
    except Exception:
        return 1

async def is_channel_banned(channel_id: int) -> bool:
    if channel_id in Config.BANNED_CHANNELS:
        return True
    return await db.is_banned_channel(channel_id)

async def is_admin(client: Client, chat_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, (await client.get_me()).id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def check_force_sub(client: Client, user_id: int) -> bool:
    if not Config.FORCE_SUB_CHANNEL:
        return True
    try:
        member = await client.get_chat_member(Config.FORCE_SUB_CHANNEL, user_id)
        return member.status not in ["left", "kicked"]
    except:
        return False

def mask_filename(filename: str) -> str:
    if len(filename) <= 8:
        return filename
    ext = ""
    if "." in filename:
        ext = "." + filename.rsplit(".", 1)[1]
        name = filename.rsplit(".", 1)[0]
    else:
        name = filename
    visible = min(4, len(name) - 4)
    return name[:visible] + "****" + ext

async def fwd_media(client: Client, message: Message):
    try:
        forwarded = await message.forward(Config.BIN_CHANNEL)
        return forwarded
    except Exception as e:
        logger.error(f"Forward error: {e}")
        return None

async def process_file(client: Client, message: Message):
    user_id = message.from_user.id

    if await is_user_banned(user_id):
        await message.reply("You are banned from using this bot.")
        return

    if not await check_force_sub(client, user_id):
        btn = await get_force_sub_button(client)
        await message.reply("Please join our channel first!", reply_markup=btn)
        return

    proc_msg = await message.reply("Processing...", quote=True)

    try:
        file_info = await get_file_info(message)
        if not file_info:
            await proc_msg.edit("Invalid file!")
            return

        fwd_msg = await fwd_media(client, message)
        if not fwd_msg:
            await proc_msg.edit("Failed to forward file!")
            return

        unique_id = str(uuid.uuid4().hex[:8])
        file_id = str(fwd_msg.id)

        await db.save_file(
            file_id=unique_id,
            message_id=fwd_msg.id,
            file_name=file_info["name"],
            file_size=file_info["size"],
            user_id=user_id,
            dc_id=await get_dc_id(client),
            file_type=file_info["type"]
        )

        await db.save_user(user_id, message.from_user.first_name, message.from_user.username)

        stream_url = f"{Config.BASE_URL()}/dl/{file_id}/{unique_id}"
        dl_url = f"{Config.BASE_URL()}/dl/{file_id}/{unique_id}?download=1"

        text = f"📄 **{file_info['name']}**\n\n"
        text += f"📥 **Download:** {dl_url}\n"
        text += f"🎬 **Stream:** {stream_url}\n\n"
        text += f"Size: `{file_info['size_text']}`"

        await proc_msg.edit(text, disable_web_page_preview=True)

        # ── Telegram log channel ─────────────────────────────────────────
        is_new_user = not await db.get_user(user_id)  # check BEFORE save_user
        if is_new_user:
            await log_newusr(client, user_id, message.from_user.first_name or "")

        await log_file_upload(
            client,
            user_id=user_id,
            user_name=message.from_user.username or message.from_user.first_name or str(user_id),
            file_name=file_info["name"],
            file_size=file_info["size_text"],
            stream_url=stream_url,
            dl_url=dl_url,
            source="private",
        )

    except Exception as e:
        logger.error(f"Process error: {e}", exc_info=True)
        await proc_msg.edit(f"Error: {str(e)}")

async def get_file_info(message: Message) -> dict:
    try:
        if message.document:
            return {
                "name": message.document.file_name or "file",
                "size": message.document.file_size,
                "size_text": format_size(message.document.file_size),
                "type": "document"
            }
        elif message.video:
            name = message.video.file_name or f"video_{message.video.file_id}.mp4"
            return {
                "name": name,
                "size": message.video.file_size,
                "size_text": format_size(message.video.file_size),
                "type": "video"
            }
        elif message.audio:
            return {
                "name": message.audio.file_name or "audio.mp3",
                "size": message.audio.file_size,
                "size_text": format_size(message.audio.file_size),
                "type": "audio"
            }
        elif message.photo:
            return {
                "name": f"photo_{message.photo.file_id}.jpg",
                "size": message.photo.file_size,
                "size_text": format_size(message.photo.file_size),
                "type": "photo"
            }
        elif message.voice:
            return {
                "name": f"voice_{message.voice.file_id}.ogg",
                "size": message.voice.file_size,
                "size_text": format_size(message.voice.file_size),
                "type": "voice"
            }
    except:
        pass
    return None

async def get_force_sub_button(client: Client):
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    try:
        chat = await client.get_chat(Config.FORCE_SUB_CHANNEL)
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel", url=chat.invite_link)]
        ])
        return btn
    except:
        return None

def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

async def handle_channel_file(client: Client, message: Message):
    if not Config.CHANNEL:
        return

    chat_id = message.chat.id

    if Config.BIN_CHANNEL and chat_id == Config.BIN_CHANNEL:
        return

    if await is_channel_banned(chat_id):
        return

    if not await is_admin(client, chat_id):
        return

    try:
        file_info = await get_file_info(message)
        if not file_info:
            return

        fwd_msg = await fwd_media(client, message)
        if not fwd_msg:
            return

        unique_id = str(uuid.uuid4().hex[:8])
        file_id = str(fwd_msg.id)

        await db.save_file(
            file_id=unique_id,
            message_id=fwd_msg.id,
            file_name=file_info["name"],
            file_size=file_info["size"],
            user_id=chat_id,
            dc_id=await get_dc_id(client),
            file_type=file_info["type"]
        )

        stream_url = f"{Config.BASE_URL()}/dl/{file_id}/{unique_id}"
        dl_url = f"{Config.BASE_URL()}/dl/{file_id}/{unique_id}?download=1"

        text = f"📄 **{file_info['name']}**\n\n"
        text += f"📥 [Download]({dl_url})\n"
        text += f"🎬 [Stream]({stream_url})"

        await message.reply(text, disable_web_page_preview=True)

        # ── Telegram log channel ─────────────────────────────────────────
        chat_title = message.chat.title or str(chat_id)
        await log_file_upload(
            client,
            user_id=chat_id,
            user_name=chat_title,
            file_name=file_info["name"],
            file_size=file_info["size_text"],
            stream_url=stream_url,
            dl_url=dl_url,
            source=f"channel:{chat_title}",
        )

    except Exception as e:
        logger.error(f"Channel file error: {e}", exc_info=True)

def setup_stream_handlers(app: Client):
    @app.on_message(filters.private & filters.incoming & FILE_TYPES)
    async def private_file_handler(client: Client, message: Message):
        await process_file(client, message)

    @app.on_message(filters.channel & filters.incoming & (filters.document | filters.video | filters.audio))
    async def channel_file_handler(client: Client, message: Message):
        await handle_channel_file(client, message)