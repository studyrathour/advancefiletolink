"""
Telegram-channel logging helpers — ported & adapted from FileToLink2.

Functions
---------
log_newusr     — notify BIN_CHANNEL when a brand-new user sends their first file
notify_owner   — send critical error alerts to OWNER_ID (+ LOG_CHANNEL if set)
log_file_upload — log every successful file upload to LOG_CHANNEL
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from pyrogram import Client
from pyrogram.errors import FloodWait

from config import Config
from utils.logger import logger


# ── helpers ────────────────────────────────────────────────────────────────────

async def _safe_send(client: Client, chat_id: int, text: str) -> None:
    """Send a message, retrying once on FloodWait."""
    try:
        await client.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await client.send_message(chat_id=chat_id, text=text, disable_web_page_preview=True)
    except Exception as exc:
        logger.warning(f"Log send failed to {chat_id}: {exc}")


# ── public API ─────────────────────────────────────────────────────────────────

async def log_newusr(client: Client, user_id: int, first_name: str) -> None:
    """
    Send a new-user notification to BIN_CHANNEL.
    Called the very first time a user uploads a file.
    (Caller is responsible for checking db.is_user_exist first.)
    """
    if not Config.BIN_CHANNEL:
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = (
        "👤 **New User**\n\n"
        f"Name : {first_name}\n"
        f"ID   : `{user_id}`\n"
        f"Time : {now}"
    )
    await _safe_send(client, Config.BIN_CHANNEL, text)


async def notify_owner(client: Client, error: str, error_id: str = "") -> None:
    """
    Send a critical-error alert to OWNER_ID.
    Also sends to LOG_CHANNEL if configured.
    """
    text = (
        "⚠️ **Critical Error**\n\n"
        f"`{error}`"
        + (f"\n\nError ID: `{error_id}`" if error_id else "")
    )
    targets = []
    if Config.OWNER_ID:
        targets.append(Config.OWNER_ID)
    if Config.LOG_CHANNEL and Config.LOG_CHANNEL not in targets:
        targets.append(Config.LOG_CHANNEL)

    await asyncio.gather(*[_safe_send(client, t, text) for t in targets], return_exceptions=True)


async def log_file_upload(
    client: Client,
    *,
    user_id: int,
    user_name: str,
    file_name: str,
    file_size: str,
    stream_url: str,
    dl_url: str,
    source: str = "private",  # "private" | "channel:<title>"
) -> None:
    """
    Log a successful file upload to LOG_CHANNEL (or BIN_CHANNEL as fallback).
    """
    channel = Config.LOG_CHANNEL or Config.BIN_CHANNEL
    if not channel:
        return

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    src_line = f"Channel : {source}" if source.startswith("channel:") else f"User    : [{user_name}](tg://user?id={user_id}) | `{user_id}`"

    text = (
        "📂 **New File Uploaded**\n\n"
        f"File    : `{file_name}`\n"
        f"Size    : `{file_size}`\n"
        f"{src_line}\n"
        f"Time    : {now}\n\n"
        f"📥 [Download]({dl_url})\n"
        f"🎬 [Stream]({stream_url})"
    )
    await _safe_send(client, channel, text)


async def log_bot_start(client: Client, bot_username: str) -> None:
    """Announce bot (re)start to LOG_CHANNEL."""
    channel = Config.LOG_CHANNEL or Config.BIN_CHANNEL
    if not channel:
        return
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = f"🚀 **Bot Started**\n\n@{bot_username}\n{now}"
    await _safe_send(client, channel, text)
