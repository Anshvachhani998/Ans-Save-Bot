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

@Client.on_message(filters.command("importusers"))
async def import_users_cmd(client, message):
    import json

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("Reply to a JSON file containing user data.")

    file = await message.reply_to_message.download()
    with open(file, "r", encoding="utf-8") as f:
        users = json.load(f)

    added = 0
    skipped = 0

    for user in users:
        try:
            user_id = int(user["id"])
            name = user["name"]

            if await db.is_user_exist(user_id):
                skipped += 1
                continue

            await db.add_user(user_id, name)
            added += 1

        except Exception as e:
            print(f"Error adding user {user}: {e}")

    await message.reply_text(
        f"✅ Import complete!\n\n**Added:** {added}\n**Skipped (already exists):** {skipped}"
    )


@Client.on_message(filters.command("userstats"))
async def user_stats(client, message):
    await message.reply("🔍 Gathering user statistics, please wait...")

    total_docs = await db.col.count_documents({})
    
    # Fetch all user_ids to count duplicates
    cursor = db.col.find({}, {"user_id": 1})
    user_ids = []
    async for doc in cursor:
        user_ids.append(doc["user_id"])

    unique_ids = set(user_ids)
    duplicates = len(user_ids) - len(unique_ids)

    reply_text = (
        f"📊 **User Statistics**\n\n"
        f"✅ Total Users in DB: {total_docs}\n"
        f"🔹 Unique Users: {len(unique_ids)}\n"
        f"⚠️ Duplicate Users: {duplicates}"
    )

    await message.reply(reply_text)
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



