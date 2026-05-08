from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

def setup_callback_handlers(app: Client):
    @app.on_callback_query()
    async def callback_handler(client: Client, query: CallbackQuery):
        data = query.data

        if data == "close":
            await query.message.delete()

        elif data.startswith("view_"):
            file_id = data.replace("view_", "")
            from config import Config
            stream_url = f"{Config.BASE_URL()}/dl/{file_id}"
            await query.answer(f"Stream URL: {stream_url}", show_alert=True)

        elif data.startswith("download_"):
            file_id = data.replace("download_", "")
            from config import Config
            dl_url = f"{Config.BASE_URL()}/dl/{file_id}?download=1"
            await query.answer(f"Download URL: {dl_url}", show_alert=True)

        await query.answer()