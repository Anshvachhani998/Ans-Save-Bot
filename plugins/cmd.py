from pyrogram import Client, filters
import os, re
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

import json
import asyncio

@Client.on_message(filters.command("remove_duplicates"))
async def remove_duplicates_cmd(client, message):
    status_msg = await message.reply("🔍 Checking for duplicate users...")

    # Fetch all users with only user_id and _id
    cursor = db.col.find({}, {"user_id": 1})
    user_ids = {}
    duplicates_count = 0

    async for doc in cursor:
        uid = doc["user_id"]
        _id = doc["_id"]

        if uid in user_ids:
            # Already seen, delete this duplicate
            await db.col.delete_one({"_id": _id})
            duplicates_count += 1
        else:
            user_ids[uid] = _id

        # Optional: update progress every 50
        if duplicates_count % 500 == 0 and duplicates_count != 0:
            await status_msg.edit(f"🔍 Removing duplicates...\nDeleted so far: {duplicates_count}")

    await status_msg.edit(f"✅ Duplicate removal complete!\nTotal duplicates removed: {duplicates_count}")


@Client.on_message(filters.command("importusers"))
async def import_users_cmd(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("Reply to a JSON file containing user data.")

    file = await message.reply_to_message.download()
    with open(file, "r", encoding="utf-8") as f:
        users = json.load(f)

    total_users = len(users)
    added = 0
    skipped = 0

    status_msg = await message.reply(f"🔄 Importing users...\n0/{total_users} processed")

    for index, user in enumerate(users, start=1):
        try:
            user_id = int(user["id"])
            name = user["name"]

            if await db.is_user_exist(user_id):
                skipped += 1
            else:
                await db.add_user(user_id, name)
                added += 1

        except Exception as e:
            print(f"Error adding user {user}: {e}")

        # Update progress every 10 users or last one
        if index % 10 == 0 or index == total_users:
            progress_text = (
                f"🔄 Importing users...\n"
                f"✅ Added: {added}\n"
                f"⚠️ Skipped: {skipped}\n"
                f"📊 Processed: {index}/{total_users}"
            )
            await status_msg.edit(progress_text)
            await asyncio.sleep(0.1)  # Small delay to avoid flood

    await status_msg.edit(
        f"🎉 Import complete!\n\n"
        f"✅ Total Added: {added}\n"
        f"⚠️ Total Skipped: {skipped}\n"
        f"📦 Total Users in File: {total_users}"
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


@Client.on_message(filters.command("add") & filters.private)
async def add_file(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /add <file_name>")
        return

    file_name = message.command[1]
    user_id = message.from_user.id
    msg_id = message.id

    success = await db.add_name(user_id, file_name, msg_id)
    if success:
        await message.reply_text(f"✅ File `{file_name}` added successfully!")
    else:
        await message.reply_text(f"⚠️ File `{file_name}` already exists in your database.")

from pyrogram.enums import ParseMode

from datetime import datetime
import re


CHANNEL_ID = -1003165005860  # replace with your channel ID

@Client.on_message(filters.command("today") & filters.private)
async def show_todays_files(client, message):
    user_id = message.from_user.id

    # 1️⃣ Fetch today's files from DB
    movies, series = await db.get_todays_files(user_id)
    
    if not movies and not series:
        await message.reply_text("❌ No files added today.")
        return

    # 2️⃣ Prepare message text (bold + clickable links)
    text = f"<b>📢 Recently Added Files List\n\n📅 Added Date: {datetime.now().strftime('%d-%m-%Y')}\n🗃️ Total Files: {len(movies)+len(series)}\n📄 Page 1/1\n\n"

    # Movies
    if movies:
        text += "🍿 Movies\n"
        for i, m in enumerate(movies, 1):
            match = re.match(r"(.+) \((.+)\)", m)
            if match:
                fname, link = match.groups()
                text += f"({i}) <a href='{link}'>{fname}</a>\n"

    # Series
    if series:
        text += "\n📺 Series\n"
        for i, s in enumerate(series, 1):
            match = re.match(r"(.+) \((.+)\)", s)
            if match:
                fname, link = match.groups()
                text += f"({i}) <a href='{link}'>{fname}</a>\n"

    text += f"\n<blockquote>Powered by - <a href='https://t.me/Ans_Links'>AnS Links 🔗</a></blockquote></b>"

    # 3️⃣ Send new message
    new_msg = await client.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    await client.pin_chat_message(CHANNEL_ID, new_msg.id, disable_notification=True)

    try:
        pin_notification_id = new_msg.id + 1  # usually comes right after pinned message
        await client.delete_messages(CHANNEL_ID, pin_notification_id)
    except:
        pass
    await message.reply_text("✅ Today's files sent and pinned in the channel.")
