import logging
from pyrogram import Client, filters
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


# Callback handler
@Client.on_callback_query()
async def settings_callbacks(client, query):
    try:
        user_id = query.from_user.id
        data = query.data
        user_session = await db.get_session(user_id)
        user_data = await db.col.find_one({"id": user_id})

        if data == "set_thumb":
            await query.message.edit_text("📷 Send me the image you want as your default thumbnail.")
        elif data == "set_caption":
            await query.message.edit_text("✍️ Send me the default caption you want for uploads.")
        elif data == "manage_channels":
            await query.message.edit_text("📂 Add or remove channels for fetching content.\nSend channel username or ID.")
        elif data == "login":
            await query.message.edit_text("🔑 Please use /login to access restricted content.")
        elif data == "my_account":
            buttons = [
                [InlineKeyboardButton("🚪 Logout", callback_data="logout")],
                [InlineKeyboardButton("📤 Upload Type", callback_data="upload_type")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_settings")]
            ]
            await query.message.edit_text("👤 My Account Menu:", reply_markup=InlineKeyboardMarkup(buttons))
        elif data == "logout":
            await db.set_session(user_id, None)
            await query.message.edit_text("✅ You have been logged out.")
        elif data == "upload_type":
            buttons = [
                [InlineKeyboardButton("📄 Document", callback_data="upload_doc"),
                 InlineKeyboardButton("🎬 Video", callback_data="upload_video")],
                [InlineKeyboardButton("⬅️ Back", callback_data="my_account")]
            ]
            await query.message.edit_text("📤 Select default upload type:", reply_markup=InlineKeyboardMarkup(buttons))
        elif data in ["upload_doc", "upload_video"]:
            upload_type = "Document" if data == "upload_doc" else "Video"
            await db.col.update_one({"id": user_id}, {"$set": {"upload_type": upload_type}})
            await query.message.edit_text(f"✅ Default upload type set to **{upload_type}**")
        elif data == "back_settings":
            await settings_cmd(client, query.message)
        elif data == "back_main":
            await query.message.edit_text("Returning to main menu...")
    except Exception as e:
        logging.error(f"Error in settings callback: {e}")
        try:
            await query.message.edit_text("❌ Something went wrong with this action.")
        except:
            pass
