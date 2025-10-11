import asyncio
import time
from pytdbot import Client, types
from info import BOT_TOKEN

# ===================== ⚙️ BOT CONFIG =====================
client = Client(
    token=BOT_TOKEN,
    api_id=8012239,
    api_hash="171e6f1bf66ed8dcc5140fbe827b6b08",
    files_directory="BotDBj",
    database_encryption_key="1234_ast$",
    td_verbosity=1,
    td_log=types.LogStreamFile("tdlib.log", 104857600),
)

# ===================== 📦 STATE HANDLER =====================
user_states = {}  # Tracks rename state per user


# ===================== 🧮 FORMAT HELPERS =====================
def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# ===================== 📊 PROGRESS UPDATER =====================
async def update_progress(message, file_name, downloaded, total, speed, is_upload=False):
    if total == 0:
        return
    percentage = (downloaded / total) * 100
    bar_length = 20
    filled = int(bar_length * downloaded / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    eta = (total - downloaded) / speed if speed > 0 else 0
    action = "⬆️ Uploading" if is_upload else "⬇️ Downloading"

    progress_text = (
        f"{action}: **{file_name}**\n\n"
        f"`{bar}` {percentage:.1f}%\n\n"
        f"📊 **Size:** {format_size(downloaded)} / {format_size(total)}\n"
        f"⚡ **Speed:** {format_size(speed)}/s\n"
        f"⏱️ **ETA:** {format_time(eta)}"
    )
    try:
        await message.edit_text(progress_text, parse_mode="markdown")
    except:
        pass


# ===================== 🤖 BOT HANDLER =====================
@client.on_message()
async def handle_message(c: Client, message: types.Message):
    if not message or not hasattr(message, "content"):
        return

    user_id = message.chat_id

    # --- Step 1: Handle rename step ---
    if user_id in user_states and user_states[user_id].get("waiting_for_name"):
        file_info = user_states[user_id]
        original_file = file_info["file"]
        file_name = file_info.get("file_name", "file")
        new_name = None

        if hasattr(message.content, "text") and hasattr(message.content.text, "text"):
            new_name = message.content.text.text
        elif hasattr(message.content, "text"):
            new_name = str(message.content.text)
        else:
            return await message.reply_text("❌ Please send a valid name!")

        status_msg = await message.reply_text("⬇️ Starting download...")

        try:
            # ---- MANUAL DOWNLOAD ----
            start_time = time.time()
            last_time = start_time
            last_downloaded = 0

            # Request download
            result = await c.invoke({
                "@type": "downloadFile",
                "file_id": original_file.id,
                "priority": 32,
                "offset": 0,
                "limit": 0,
                "synchronous": False,
            })
            file_id = result.id if hasattr(result, "id") else result.get("id")

            while True:
                file_info_update = await c.invoke({"@type": "getFile", "file_id": file_id})

                if hasattr(file_info_update.local, "is_downloading_completed") and file_info_update.local.is_downloading_completed:
                    await update_progress(status_msg, file_name, file_info_update.expected_size, file_info_update.expected_size, 0)
                    break

                downloaded = getattr(file_info_update.local, "downloaded_size", 0)
                total = getattr(file_info_update, "expected_size", 0)

                now = time.time()
                time_diff = now - last_time
                speed = (downloaded - last_downloaded) / time_diff if time_diff > 0 else 0
                await update_progress(status_msg, file_name, downloaded, total, speed)
                last_time = now
                last_downloaded = downloaded

                await asyncio.sleep(0.5)

            downloaded_path = file_info_update.local.path

            # ---- UPLOAD WITH PROGRESS ----
            await status_msg.edit_text("⬆️ Starting upload...")

            caption = f"✅ ʀᴇɴᴀᴍᴇᴅ ᴛᴏ: **{new_name}**"
            input_content = None

            if file_info["type"] == "document":
                input_content = {
                    "@type": "inputMessageDocument",
                    "document": {"@type": "inputFileLocal", "path": downloaded_path},
                    "caption": {"@type": "formattedText", "text": caption},
                }
            elif file_info["type"] == "photo":
                input_content = {
                    "@type": "inputMessagePhoto",
                    "photo": {"@type": "inputFileLocal", "path": downloaded_path},
                    "caption": {"@type": "formattedText", "text": caption},
                }
            elif file_info["type"] == "video":
                input_content = {
                    "@type": "inputMessageVideo",
                    "video": {"@type": "inputFileLocal", "path": downloaded_path},
                    "caption": {"@type": "formattedText", "text": caption},
                }
            elif file_info["type"] == "audio":
                input_content = {
                    "@type": "inputMessageAudio",
                    "audio": {"@type": "inputFileLocal", "path": downloaded_path},
                    "caption": {"@type": "formattedText", "text": caption},
                }

            if input_content:
                await c.invoke({
                    "@type": "sendMessage",
                    "chat_id": user_id,
                    "input_message_content": input_content,
                })

            await status_msg.edit_text(f"✅ File renamed successfully to: **{new_name}**", parse_mode="markdown")

        except Exception as e:
            await status_msg.edit_text(f"❌ Error: {str(e)}")

        finally:
            user_states.pop(user_id, None)
        return

    # --- Step 2: Handle media files ---
    content = message.content
    file_info, file_type, file_name = None, None, None

    if hasattr(content, "document"):
        file_info = content.document.document
        file_name = content.document.file_name
        file_type = "document"
    elif hasattr(content, "photo"):
        file_info = content.photo.sizes[-1].photo
        file_name = f"photo_{message.id}.jpg"
        file_type = "photo"
    elif hasattr(content, "video"):
        file_info = content.video.video
        file_name = content.video.file_name
        file_type = "video"
    elif hasattr(content, "audio"):
        file_info = content.audio.audio
        file_name = content.audio.file_name
        file_type = "audio"

    if file_info:
        user_states[user_id] = {
            "file": file_info,
            "type": file_type,
            "file_name": file_name,
            "waiting_for_name": True,
        }

        await message.reply_text(
            f"📁 **Current file name:** `{file_name}`\n\n"
            f"📝 Send me the new name for this file.",
            parse_mode="markdown",
        )
        return

    # --- Step 3: Handle /start command ---
    if hasattr(message.content, "text") and hasattr(message.content.text, "text"):
        text = message.content.text.text
        if text == "/start":
            await message.reply_text(
                "👋 ʜᴇʟʟᴏ, ɪ ᴀᴍ **ÀstràDev Assistant!**\n\n"
                "📤 Send me any media file to rename it with progress tracking.\n"
                "💠 Built with pytdbot ⚙️",
                parse_mode="markdown",
            )


# ===================== 🚀 START BOT =====================
if __name__ == "__main__":
    print("⚡ ÀstràDev Assistant is now running...")
    client.run()      
