import time
import psutil
import speedtest
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
import database as db
from plugins.stream import is_user_banned

async def is_owner(user_id: int) -> bool:
    return user_id == Config.OWNER_ID

def setup_common_handlers(app: Client):
    @app.on_message(filters.command("start"))
    async def start_handler(client: Client, message: Message):
        await message.reply(
            "👋 **Welcome to File2Link Bot!**\n\n"
            "Send me any file and I'll generate a direct download/stream link for you.\n\n"
            "**Commands:**\n"
            "/link - Generate link (reply to file)\n"
            "/ping - Check bot latency\n"
            "/stats - View bot statistics\n"
            "/help - Show help\n\n"
            "Bot by @yourusername"
        )

    @app.on_message(filters.command("help"))
    async def help_handler(client: Client, message: Message):
        await message.reply(
            "📖 **Help**\n\n"
            "**How to use:**\n"
            "1. Send any file to the bot\n"
            "2. Wait for processing\n"
            "3. Get your download/stream link\n\n"
            "**Commands:**\n"
            "/start - Start the bot\n"
            "/link - Generate link (reply to file)\n"
            "/ping - Check latency\n"
            "/stats - View statistics\n"
            "/help - Show this help"
        )

    @app.on_message(filters.command("ping"))
    async def ping_handler(client: Client, message: Message):
        start = time.time()
        msg = await message.reply("Pinging...")
        end = time.time()
        latency = (end - start) * 1000
        await msg.edit(f"🏓 **Pong!**\nLatency: `{latency:.2f}ms`")

    @app.on_message(filters.command("stats"))
    async def stats_handler(client: Client, message: Message):
        try:
            file_stats = await db.get_file_stats()
            user_count = await db.get_user_count()

            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            text = f"📊 **Bot Statistics**\n\n"
            text += f"**Files:**\n"
            text += f"├ Total Files: `{file_stats['total_files']}`\n"
            text += f"├ Total Downloads: `{file_stats['total_downloads']}`\n\n"
            text += f"**Users:**\n"
            text += f"├ Total Users: `{user_count}`\n\n"
            text += f"**System:**\n"
            text += f"├ CPU: `{cpu}%`\n"
            text += f"├ RAM: `{memory.percent}%`\n"
            text += f"└ Disk: `{disk.percent}%`"

            await message.reply(text)
        except Exception as e:
            await message.reply(f"Error getting stats: {str(e)}")

    @app.on_message(filters.command("speedtest"))
    async def speedtest_handler(client: Client, message: Message):
        if not await is_owner(message.from_user.id):
            return

        msg = await message.reply("Running speed test...")
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download = st.download() / 1024 / 1024
            upload = st.upload() / 1024 / 1024

            await msg.edit(
                f"⚡ **Speed Test Results**\n\n"
                f"📥 Download: `{download:.2f} Mbps`\n"
                f"📤 Upload: `{upload:.2f} Mbps`"
            )
        except Exception as e:
            await msg.edit(f"Speed test failed: {str(e)}")

    @app.on_message(filters.command("dc"))
    async def dc_handler(client: Client, message: Message):
        from plugins.stream import get_dc_id
        dc = await get_dc_id(client)
        await message.reply(
            f"📡 **Data Center Info**\n\n"
            f"DC ID: `{dc}`\n"
            f"Bot ID: `{(await client.get_me()).id}`"
        )

    @app.on_message(filters.command("link"))
    async def link_handler(client: Client, message: Message):
        if not message.reply_to_message:
            await message.reply("Reply to a file to generate link!")
            return

        from plugins.stream import process_file
        await process_file(client, message.reply_to_message)

    @app.on_message(filters.command("status"))
    async def status_handler(client: Client, message: Message):
        try:
            from streamer import streamer
            if streamer:
                workloads = streamer.work_loads
                text = "⚙️ **Client Status**\n\n"
                for idx, workload in workloads.items():
                    text += f"Client {idx}: `{workload} active downloads`\n"
                await message.reply(text)
            else:
                await message.reply("Streamer not initialized!")
        except Exception as e:
            await message.reply(f"Error: {str(e)}")

    @app.on_message(filters.command("about"))
    async def about_handler(client: Client, message: Message):
        await message.reply(
            "ℹ️ **File2Link Bot**\n\n"
            "A fast Telegram file to link converter.\n\n"
            "Features:\n"
            "• Fast streaming via raw API\n"
            "• Multi-client support\n"
            "• User management\n"
            "• Admin panel\n"
            "• And more..."
        )