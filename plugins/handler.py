
import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from info import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION
from database.db import db
from plugins.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}


@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/kingvj01")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_botz')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
import asyncio

import asyncio, os, math, time
from pyrogram import Client, enums
from pyrogram.types import Message


async def progress(current, total, status_message: Message, stage: str):
    import time

    now = time.time()
    if not hasattr(status_message, "start_time"):
        status_message.start_time = now
    diff = now - status_message.start_time
    if diff == 0:
        diff = 1

    speed = current / diff
    percentage = current * 100 / total
    eta = round((total - current) / speed) if speed > 0 else 0

    bar_length = 20
    filled = int(bar_length * percentage / 100)
    bar = "▰" * filled + "▱" * (bar_length - filled)

    msg_text = (
        f"**{stage.capitalize()} Progress** 📥📤\n\n"
        f"{bar} `{percentage:.1f}%`\n"
        f"**Speed:** {humanbytes(speed)}/s\n"
        f"**Done:** {humanbytes(current)} / {humanbytes(total)}\n"
        f"**ETA:** {time_formatter(eta)}"
    )

    # Edit every 2-3 sec to avoid flood
    if not hasattr(status_message, "last_edit") or (now - status_message.last_edit) > 3:
        try:
            await status_message.edit_text(msg_text)
            status_message.last_edit = now
        except:
            pass


def humanbytes(size):
    # Convert bytes to human readable
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    Dic_powerN = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {Dic_powerN[n]}"


def time_formatter(seconds):
    # Convert seconds to human-readable time
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{days}d, " if days else "")
        + (f"{hours}h, " if hours else "")
        + (f"{minutes}m, " if minutes else "")
        + (f"{seconds}s" if seconds else "")
    )
    return tmp



async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    # Joining chats (for invite links)
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:

        if TechVJUser is None:
            await client.send_message(
                message.chat.id,
                "**String Session is not Set**",
                reply_to_message_id=message.id
            )
            return

        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e:
                await client.send_message(
                    message.chat.id,
                    f"**Error** : __{e}__",
                    reply_to_message_id=message.id
                )
                return

            await client.send_message(
                message.chat.id,
                "**Chat Joined Successfully ✅**",
                reply_to_message_id=message.id
            )

        except UserAlreadyParticipant:
            await client.send_message(
                message.chat.id,
                "**Chat already Joined**",
                reply_to_message_id=message.id
            )

        except InviteHashExpired:
            await client.send_message(
                message.chat.id,
                "**Invalid Link**",
                reply_to_message_id=message.id
            )

    # Handling message links
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text(
                "**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**"
            )

        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())

        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            acc = None

            # 🟢 PRIVATE or BOT LINKS (need login/session)
            if "https://t.me/c/" in message.text or "https://t.me/b/" in message.text:
                if LOGIN_SYSTEM == True:
                    user_data = await db.get_session(message.from_user.id)
                    if user_data is None:
                        await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                        batch_temp.IS_BATCH[message.from_user.id] = True
                        return

                    try:
                        acc = Client(
                            "saverestricted",
                            session_string=user_data,
                            api_hash=API_HASH,
                            api_id=API_ID
                        )
                        await acc.start()
                    except Exception:
                        batch_temp.IS_BATCH[message.from_user.id] = True
                        return await message.reply(
                            "**Your Login Session Expired. So /logout First Then Login Again By - /login**"
                        )
                else:
                    if TechVJUser is None:
                        batch_temp.IS_BATCH[message.from_user.id] = True
                        await client.send_message(
                            message.chat.id,
                            "**String Session is not Set**",
                            reply_to_message_id=message.id
                        )
                        return
                    acc = TechVJUser

                # Private chat link
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])
                    try:
                        await handle_private(client, acc, message, chatid, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(
                                message.chat.id,
                                f"Error: {e}",
                                reply_to_message_id=message.id
                            )

                # Bot link
                elif "https://t.me/b/" in message.text:
                    username = datas[4]
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(
                                message.chat.id,
                                f"Error: {e}",
                                reply_to_message_id=message.id
                            )

            # 🔵 PUBLIC LINKS (no login/session needed)
            else:
                username = datas[3]
                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(
                        message.chat.id,
                        "The username is not occupied by anyone.",
                        reply_to_message_id=message.id
                    )
                    return

                try:
                    await client.copy_message(
                        message.chat.id,
                        msg.chat.id,
                        msg.id,
                        reply_to_message_id=message.id
                    )
                except Exception:
                    try:
                        if TechVJUser:
                            await handle_private(client, TechVJUser, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(
                                message.chat.id,
                                f"Error: {e}",
                                reply_to_message_id=message.id
                            )

            # Wait before next message (avoid FloodWait)
            await asyncio.sleep(3)

        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        if msg is None or msg.empty:
            return
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error getting message: {e}", reply_to_message_id=message.id)
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    chat = message.chat.id

    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    # 📩 Text Message
    if msg_type == "Text":
        try:
            await client.send_message(
                chat, msg.text, entities=msg.entities,
                reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)
        return

    # 🟢 Prepare download folder
    user_download_dir = f"downloads/{message.from_user.id}"
    os.makedirs(user_download_dir, exist_ok=True)

    # Use original filename if exists
    filename = getattr(msg.document or msg.video or msg.audio, "file_name", f"{msg.id}_file")
    file_path = os.path.join(user_download_dir, filename)

    # Show downloading status
    smsg = await client.send_message(chat, "**Downloading...**", reply_to_message_id=message.id)

    # Download the file
    try:
        file = await acc.download_media(
            msg,
            file_name=file_path,
            progress=progress,
            progress_args=[smsg, "download"],
            in_memory=False
        )
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"Error downloading: {e}", reply_to_message_id=message.id)
        await smsg.delete()
        return

    # Upload the file
    caption = getattr(msg, "caption", None)
    thumb = None

    try:
        if msg_type == "Document":
            if getattr(msg.document, "thumbs", None):
                try:
                    thumb = await acc.download_media(msg.document.thumbs[0].file_id)
                except: pass
            await client.send_document(
                chat, file, thumb=thumb, caption=caption,
                reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                progress=progress, progress_args=[smsg, "upload"]
            )

        elif msg_type == "Video":
            if getattr(msg.video, "thumbs", None):
                try:
                    thumb = await acc.download_media(msg.video.thumbs[0].file_id)
                except: pass
            await client.send_video(
                chat, file, duration=msg.video.duration, width=msg.video.width,
                height=msg.video.height, thumb=thumb, caption=caption,
                reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                progress=progress, progress_args=[smsg, "upload"]
            )

        elif msg_type == "Animation":
            await client.send_animation(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif msg_type == "Sticker":
            await client.send_sticker(chat, file, reply_to_message_id=message.id)

        elif msg_type == "Voice":
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[smsg, "upload"])

        elif msg_type == "Audio":
            if getattr(msg.audio, "thumbs", None):
                try:
                    thumb = await acc.download_media(msg.audio.thumbs[0].file_id)
                except: pass
            await client.send_audio(chat, file, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[smsg, "upload"])

        elif msg_type == "Photo":
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"Error uploading: {e}", reply_to_message_id=message.id)

    finally:
        # Cleanup
        if os.path.exists(file):
            os.remove(file)
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
        # Delete the progress message
        try:
            await smsg.delete()
        except: pass

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        
