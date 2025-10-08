import os
import asyncio
import logging
from mtcute import TelegramClient
from mtcute.errors import MtcpRpcError

from info import API_ID, API_HASH, USER_SESSION  # TELETHON user session

# ------------------- Logging setup -------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ------------------- MTCute client -------------------
mt_client = TelegramClient(USER_SESSION, API_ID, API_HASH)


async def mt_download(media_msg, output_path):
    """
    Super-fast download using MTCute with logging
    """
    try:
        async with mt_client:
            logging.info(f"📥 Starting download to: {output_path}")
            await mt_client.download_media(media_msg.media, file_name=output_path)
            logging.info(f"✅ Download complete: {output_path}")
    except MtcpRpcError as e:
        logging.error(f"❌ Download failed: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error during download: {e}")
    return output_path


async def mt_upload(file_path):
    """
    Super-fast upload using MTCute with logging
    """
    try:
        async with mt_client:
            logging.info(f"📤 Starting upload: {file_path}")
            uploaded = await mt_client.upload_file(file_path)
            logging.info(f"✅ Upload complete: {file_path}")
            return uploaded
    except MtcpRpcError as e:
        logging.error(f"❌ Upload failed: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error during upload: {e}")

