import os
import asyncio
from telethon.sessions import StringSession
from telethon import TelegramClient
from fasttelethon import download_file, upload_file
from info import API_ID, API_HASH, USER_SESSION

fast_client = TelegramClient(StringSession(USER_SESSION), API_ID, API_HASH)

async def fast_download(media_msg, output_path):
    """
    Super-fast file download using FastTelethon
    """
    async with fast_client:
        await download_file(fast_client, media_msg.media, output_path)
    return output_path


async def fast_upload(file_path):
    """
    Super-fast file upload using FastTelethon
    """
    async with fast_client:
        uploaded = await upload_file(fast_client, file_path)
    return uploaded
