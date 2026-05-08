from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
import database as db

async def is_owner(user_id: int) -> bool:
    return user_id == Config.OWNER_ID

async def is_authorized_user(user_id: int) -> bool:
    if await is_owner(user_id):
        return True
    return await db.is_authorized(user_id)

def setup_admin_handlers(app: Client):
    @app.on_message(filters.command("ban"))
    async def ban_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("Usage: /ban <user_id or channel_id> [reason]")
            return

        try:
            target = int(message.command[1])
            reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason"

            if message.chat.type == "channel" or message.chat.type == "supergroup":
                await db.ban_channel(target, reason)
                await message.reply(f"Channel `{target}` has been banned!")
                try:
                    await client.leave_chat(target)
                except:
                    pass
            else:
                await db.ban_user(target, reason)
                await message.reply(f"User `{target}` has been banned!")

        except ValueError:
            await message.reply("Invalid user/channel ID!")

    @app.on_message(filters.command("unban"))
    async def unban_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("Usage: /unban <user_id or channel_id>")
            return

        try:
            target = int(message.command[1])
            await db.unban_user(target)
            await db.unban_channel(target)
            await message.reply(f"`{target}` has been unbanned!")
        except ValueError:
            await message.reply("Invalid user/channel ID!")

    @app.on_message(filters.command("authorize"))
    async def authorize_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("Usage: /authorize <user_id>")
            return

        try:
            target = int(message.command[1])
            await db.authorize_user(target)
            await message.reply(f"User `{target}` has been authorized!")
        except ValueError:
            await message.reply("Invalid user ID!")

    @app.on_message(filters.command("deauthorize"))
    async def deauthorize_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        if len(message.command) < 2:
            await message.reply("Usage: /deauthorize <user_id>")
            return

        try:
            target = int(message.command[1])
            await db.deauthorize_user(target)
            await message.reply(f"User `{target}` authorization removed!")
        except ValueError:
            await message.reply("Invalid user ID!")

    @app.on_message(filters.command("listauth"))
    async def listauth_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        users = await db.get_authorized_users()
        if not users:
            await message.reply("No authorized users!")
            return

        text = "**Authorized Users:**\n\n"
        for user in users:
            text += f"- `{user['user_id']}`\n"
        await message.reply(text)

    @app.on_message(filters.command("users"))
    async def users_count_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        count = await db.get_user_count()
        await message.reply(f"Total users: **{count}**")

    @app.on_message(filters.command("broadcast"))
    async def broadcast_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        if not message.reply_to_message:
            await message.reply("Reply to a message to broadcast!")
            return

        users = await db.get_all_users()
        success = 0
        failed = 0

        await message.reply(f"Broadcasting to {len(users)} users...")

        for user in users:
            try:
                await message.reply_to_message.copy(int(user["user_id"]))
                success += 1
            except:
                failed += 1

        await message.reply(f"Broadcast complete!\nSuccess: {success}\nFailed: {failed}")

    @app.on_message(filters.command("restart"))
    async def restart_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        await message.reply("Restarting...")
        import os
        os.system("restart")

    @app.on_message(filters.command("log"))
    async def log_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        import glob
        log_files = glob.glob("*.log")
        if not log_files:
            await message.reply("No log files found!")
            return

        with open(log_files[0], "r") as f:
            lines = f.readlines()[-50:]
            await message.reply("".join(lines))

    @app.on_message(filters.command("banned"))
    async def banned_list_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        users = await db.get_banned_users()
        if not users:
            await message.reply("No banned users!")
            return

        text = "**Banned Users:**\n\n"
        for user in users:
            reason = user.get("reason", "No reason")
            text += f"- `{user['user_id']}` - {reason}\n"
        await message.reply(text)