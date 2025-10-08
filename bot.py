import os
import logging
import asyncio
import pytz
from datetime import date, datetime
from aiohttp import web
from pytdbot import Client, types

from plugins import web_server
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT, ADMINS

# ------------------- Logging setup -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pytdbot")
logger.setLevel(logging.INFO)

# ------------------- Directories -------------------
DOWNLOAD_DIR = "/app/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ------------------- Pytdbot client -------------------
client = Client(token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH, files_directory="BotDB", database_encryption_key="sdsffsfafss")

# ------------------- Fast download -------------------
async def fast_download(message, output_path):
    try:
        logger.info(f"📥 Starting download: {output_path}")
        file_path = await message.download_file(output_path)
        logger.info(f"✅ Download complete: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return None

# ------------------- Fast upload -------------------
async def fast_upload(message, file_path):
    try:
        logger.info(f"📤 Starting upload: {file_path}")
        await message.reply_document(file_path)
        logger.info(f"✅ Upload complete: {file_path}")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")

# ------------------- Bot startup log -------------------
async def on_startup():
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")

    await client.send_message(LOG_CHANNEL, f"✅ Bot Restarted! 📅 Date: {today} 🕒 Time: {time_str}")
    logger.info(f"🤖 Bot started and logged to {LOG_CHANNEL}")

    # Start web server
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    site = web.TCPSite(app_runner, "0.0.0.0", PORT)
    await site.start()
    logger.info(f"🌐 Web Server Running on PORT {PORT}")

# ------------------- Message handlers -------------------

@client.on_message(filters=types.InputTextMessageContent)  # Text messages
async def start_command(message: types.Message):
    if message.text and message.text.lower() == "/start":
        await client.send_message(
            chat_id=message.chat.id,
            text="👋 Hello! I am your fast Telegram bot.\n\nUse /fastdl to download media quickly."
        )
        
# ------------------- Run client -------------------
async def main():
    await client.start()
    await on_startup()
    logger.info("Bot is idle...")
    await client.idle()  # Keep bot running

asyncio.run(main())
