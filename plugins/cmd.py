from pyrogram import Client, filters
import os
import time
import logging 
import aiohttp
import requests
import asyncio
import subprocess
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import LOG_CHANNEL, ADMINS, BOT_TOKEN

from pyrogram.types import Message
import json, os
from datetime import datetime
from database.db import db 

@Client.on_message(filters.command("import") & filters.reply)
async def import_users_cmd(client, message):
    reply = message.reply_to_message

    # Check if JSON file reply me diya gaya hai
    if not reply.document or not reply.document.file_name.endswith(".json"):
        return await message.reply("⚠️ Reply me ek valid `.json` file bhej bhai!")

    try:
        # File download karo
        file_path = await reply.download()
        with open(file_path, "r") as f:
            data = json.load(f)

        added = 0
        skipped = 0

        for user in data:
            try:
                user_id = int(user["id"])
                name = user.get("name", "Unknown")

                # Check if user already exist
                if await db.is_user_exist(user_id):
                    skipped += 1
                    continue

                # Add new user
                await db.add_user(user_id, name)
                added += 1
            except Exception as e:
                print(f"Error adding user {user}: {e}")
                continue

        await message.reply(
            f"✅ **Import Completed Successfully!**\n\n👥 **Added:** {added}\n⏭️ **Skipped:** {skipped}"
        )

    except Exception as e:
        await message.reply(f"❌ Error reading JSON file:\n`{e}`")

@Client.on_message(filters.command("restart"))
async def git_pull(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply_text("🚫 **You are not authorized to use this command!**")
      
    working_directory = "/user1/ubuntu/Ans-Save-Bot"

    process = subprocess.Popen(
        "git pull https://github.com/Anshvachhani998/Ans-Save-Bot",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE

    )

    stdout, stderr = process.communicate()
    output = stdout.decode().strip()
    error = stderr.decode().strip()
    cwd = os.getcwd()
    logging.info("Raw Output (stdout): %s", output)
    logging.info("Raw Error (stderr): %s", error)

    if error and "Already up to date." not in output and "FETCH_HEAD" not in error:
        await message.reply_text(f"❌ Error occurred: {os.getcwd()}\n{error}")
        logging.info(f"get dic {cwd}")
        return

    if "Already up to date." in output:
        await message.reply_text("🚀 Repository is already up to date!")
        return
      
    if any(word in output.lower() for word in [
        "updating", "changed", "insert", "delete", "merge", "fast-forward",
        "files", "create mode", "rename", "pulling"
    ]):
        await message.reply_text(f"📦 Git Pull Output:\n```\n{output}\n```")
        await message.reply_text("🔄 Git Pull successful!\n♻ Restarting bot...")

        subprocess.Popen("bash /user1/ubuntu/Ans-Save-Bot/start.sh", shell=True)
        os._exit(0)

    await message.reply_text(f"📦 Git Pull Output:\n```\n{output}\n```")



