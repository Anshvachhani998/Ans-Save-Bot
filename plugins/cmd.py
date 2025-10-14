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
from database import db

@Client.on_message(filters.command("import_users") & filters.reply)
async def import_users_cmd(client: Client, message: Message):
    """Import users from a replied JSON file into database"""
    replied = message.reply_to_message

    if not replied or not replied.document:
        return await message.reply("⚠️ Please reply to a valid JSON file (new_users.json).")

    # download file
    file_path = await replied.download()
    await message.reply("📥 JSON file received, importing users...")

    try:
        # load JSON
        with open(file_path, "r", encoding="utf-8") as f:
            users = json.load(f)

        if not isinstance(users, list):
            return await message.reply("❌ Invalid JSON format! Expected a list of users.")

        added, skipped = 0, 0
        for u in users:
            uid = u.get("id")
            name = u.get("name")

            if not uid or not name:
                skipped += 1
                continue

            # check if already exists
            existing = await db.col.find_one({"user_id": int(uid)})
            if existing:
                skipped += 1
                continue

            # add user
            await db.add_user(int(uid), name)
            added += 1

            # progress feedback every 20 users
            if added % 20 == 0:
                await message.edit_text(f"⏳ Imported so far: {added} users...")

        await message.reply(
            f"✅ Import Completed!\n\n"
            f"👤 Added: {added}\n"
            f"⚙️ Skipped (already exists/invalid): {skipped}"
        )

    except Exception as e:
        await message.reply(f"❌ Import failed: `{e}`")

    finally:
        # cleanup downloaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            

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



