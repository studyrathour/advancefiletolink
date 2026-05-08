from functools import wraps
from pyrogram.types import Message
from config import Config
import database as db

async def check_banned(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id if message.from_user else 0
        if await db.is_banned_user(user_id):
            await message.reply("You are banned!")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

async def check_auth(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id if message.from_user else 0
        if Config.TOKEN_ENABLED and not await is_owner_or_auth(user_id):
            await message.reply("Authentication required!")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

async def is_owner_or_auth(user_id: int) -> bool:
    if user_id == Config.OWNER_ID:
        return True
    if await db.is_authorized(user_id):
        return True
    return False

def admin_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id if message.from_user else 0
        if user_id != Config.OWNER_ID:
            await message.reply("Admin only!")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper