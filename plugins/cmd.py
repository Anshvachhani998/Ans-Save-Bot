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




import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import db  # tumhara DB class

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# /settings command
@Client.on_message(filters.command("settings"))
async def settings_cmd(client, message):
    try:
        user_id = message.from_user.id
        user_session = await db.get_session(user_id)
        user_data = await db.col.find_one({"id": user_id})

        if user_session:  # Logged in
            account_btn = InlineKeyboardButton("👤 My Account", callback_data="my_account")
        else:  # Not logged in
            account_btn = InlineKeyboardButton("🔑 Login", callback_data="login")

        buttons = [
            [InlineKeyboardButton("🖼 Change Thumbnail", callback_data="set_thumb")],
            [InlineKeyboardButton("✍️ Change Caption", callback_data="set_caption")],
            [InlineKeyboardButton("📂 Manage Channels", callback_data="manage_channels")],
            [account_btn],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_main")]
        ]
        await message.reply_text(
            "**⚙️ User Settings Menu:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        logging.error(f"Error in /settings command: {e}")
        await message.reply_text("❌ Something went wrong while opening settings.")


