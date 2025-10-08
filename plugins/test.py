from pyrogram import Client, filters
from plugins.login import fast_download, fast_upload

@Client.on_message(filters.command("fastdl"))
async def handle_fast_download(bot, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.reply("❌ Reply to a media message to download it fast!")

    file_name = "downloads/fast_" + str(reply.id) + ".mp4"
    await message.reply("⏳ Downloading with FastTelethon...")

    # Fast download
    await fast_download(reply, file_name)
    await message.reply(f"✅ Downloaded: {file_name}")

@Client.on_message(filters.command("fastup"))
async def handle_fast_upload(bot, message):
    file_path = "downloads/sample.mp4"
    await message.reply("📤 Uploading super-fast...")

    uploaded = await fast_upload(file_path)
    await message.reply("✅ Upload done using FastTelethon!")
