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
# ------------------- /start command -------------------
@client.on_message()
async def handle_start(_: Client, message: types.Message):
    if isinstance(message.content, types.MessageText):
        if message.text.lower() == "/start":
            await message.reply_text(
                "👋 Hello! I am your fast Pytdbot bot.\n\nUse /fastdl to download media quickly."
            )
# ------------------- Message handlers -------------------
@client.on_message()
async def handle_messages(_: Client, message: types.Message):
    # ---------------- Fast download ----------------
    if message.text and message.text.startswith("/fastdl"):
        if not getattr(message, "reply_to_message_id", None):
            await message.reply_text("❌ Reply to a media message to download it!")
            return

        # Replyed message content
        reply_id = message.reply_to_message_id
        chat_id = message.chat.id

        # TDLib me getMessage use karke replied message lo
        reply_update = await _.invoke({
            "@type": "getMessage",
            "chat_id": chat_id,
            "message_id": reply_id
        })

        # File id nikalna
        file_id = None
        content_type = reply_update.get("content", {}).get("@type", "")
        if content_type == "messageDocument":
            file_id = reply_update["content"]["document"]["id"]
        elif content_type == "messageVideo":
            file_id = reply_update["content"]["video"]["id"]
        elif content_type == "messagePhoto":
            # last size ka photo id
            file_id = reply_update["content"]["sizes"][-1]["photo"]["id"]
        else:
            await message.reply_text("❌ Unsupported media type")
            return

        file_name = os.path.join(DOWNLOAD_DIR, f"fast_{reply_id}.mp4")
        await message.reply_text("⏳ Downloading...")

        try:
            file_info = await _.downloadFile(file_id=file_id, priority=1, synchronous=True)
            downloaded_path = file_info.local.path
            await message.reply_text(f"✅ Downloaded: {downloaded_path}")
        except Exception as e:
            await message.reply_text(f"❌ Failed to download: {e}")

    # ---------------- Fast upload ----------------
    elif message.text and message.text.startswith("/fastup"):
        file_path = os.path.join(DOWNLOAD_DIR, "sample.mp4")  # replace with actual file
        await message.reply_text("📤 Uploading...")
        await fast_upload(message, file_path)

# ------------------- Run bot -------------------
if __name__ == "__main__":
    client.run()
