import os
import logging
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
client = Client(
    token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    files_directory="BotDB",
    database_encryption_key="sdsffsfafss"
)

# ------------------- Fast download/upload -------------------
async def fast_download(message, output_path):
    try:
        logger.info(f"📥 Starting download: {output_path}")
        file_path = await message.download_file(output_path)
        logger.info(f"✅ Download complete: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        return None

async def fast_upload(message, file_path):
    try:
        logger.info(f"📤 Starting upload: {file_path}")
        await client.send_document(
            chat_id=message.chat.id,
            document=file_path,
            caption="✅ Upload complete"
        )
        logger.info(f"✅ Upload complete: {file_path}")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")

# ------------------- /start command -------------------
@client.on_message()
async def handle_start(client, update):
    message = update.message
    if message.text and message.text.lower() == "/start":
        await client.send_message(
            chat_id=message.chat.id,
            text=types.InputMessageText(
                text="👋 Hello! I am your fast Pytdbot bot.\n\nUse /fastdl to download media quickly."
            )
        )

# ------------------- Message handlers -------------------
@client.on_message()
async def handle_messages(client, update):
    message = update.message

    # Fast download command
    if message.text and message.text.startswith("/fastdl") and message.reply_to_message:
        reply = message.reply_to_message
        if not reply.document and not reply.photo and not reply.video:
            await client.send_message(
                chat_id=message.chat.id,
                text=types.InputMessageText("❌ Reply to a media message to download it!")
            )
            return
        file_name = os.path.join(DOWNLOAD_DIR, f"fast_{reply.id}.mp4")
        await client.send_message(chat_id=message.chat.id, text=types.InputMessageText("⏳ Downloading..."))
        await fast_download(reply, file_name)
        await client.send_message(chat_id=message.chat.id, text=types.InputMessageText(f"✅ Downloaded: {file_name}"))

    # Fast upload command
    if message.text and message.text.startswith("/fastup"):
        file_path = os.path.join(DOWNLOAD_DIR, "sample.mp4")  # replace with actual file
        await client.send_message(chat_id=message.chat.id, text=types.InputMessageText("📤 Uploading..."))
        await fast_upload(message, file_path)

# ------------------- Run bot -------------------
if __name__ == "__main__":
    client.run()
