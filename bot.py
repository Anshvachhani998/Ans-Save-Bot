import logging
import os
import asyncio
import re
from datetime import date, datetime, timedelta
import pytz

from pyrogram import Client, __version__, types, utils as pyroutils
from pyrogram.raw.all import layer
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from aiohttp import web

from plugins import web_server
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT
from database.db import db

try:
    from info import STRING_SESSION, LOGIN_SYSTEM
except Exception:
    STRING_SESSION = None
    LOGIN_SYSTEM = False

# adjust pyrogram minimum ids if needed
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

# Logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

CHANNEL_ID = -1003165005860

# Helper: split text into 4000-char chunks
def split_text(text: str, limit: int = 4000):
    chunks = []
    while len(text) > limit:
        idx = text.rfind("\n", 0, limit)
        if idx == -1:
            idx = limit
        chunks.append(text[:idx])
        text = text[idx:]
    chunks.append(text)
    return chunks

# Nightly update task
async def nightly_update(client):
    user_id = 7298944577  # Single user ID
    while True:
        now = datetime.now()
        # Calculate seconds until next midnight
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        wait_seconds = (next_midnight - now).total_seconds()
        logging.info(f"🕒 Waiting {wait_seconds} seconds until midnight for nightly update")
        await asyncio.sleep(wait_seconds)

        logging.info("🕒 Nightly update iteration started")

        # Use previous day to fetch files (so we get 'today's' files for the day that just ended)
        previous_day = datetime.now().date() - timedelta(days=1)
        logging.info(f"🔹 Fetching files for user_id: {user_id} and date: {previous_day}")

        combined_movies, combined_series = await db.get_todays_files(user_id, previous_day)
        logging.info(f"📂 Found {len(combined_movies)} movies and {len(combined_series)} series")

        if not combined_movies and not combined_series:
            logging.info("ℹ️ No new files to send, skipping this iteration")
            continue

        # Prepare professional full-bold text
        lines = []
        lines.append("<b>📢 Hey there! Here's your Daily Media Update 🎉</b>\n")
        lines.append(f"<b>📆 Date:</b> <b>{previous_day.strftime('%d-%m-%Y')}</b>")
        lines.append(f"<b>🗂️ Total Files:</b> <b>{len(combined_movies) + len(combined_series)}</b>\n")

        if combined_movies:
            lines.append("<b>🔥 New Movies:</b>")
            for i, m in enumerate(combined_movies, 1):
                match = re.match(r"(.+) \((.+)\)", m)
                if match:
                    fname, link = match.groups()
                    link = link.replace("\n", "").replace("\r", "")
                    lines.append(f"<b>🎬 ({i}) <a href='{link}'>{fname}</a></b>")

        if combined_series:
            lines.append("\n<b>📺 New Series:</b>")
            for i, s in enumerate(combined_series, 1):
                match = re.match(r"(.+) \((.+)\)", s)
                if match:
                    fname, link = match.groups()
                    link = link.replace("\n", "").replace("\r", "")
                    lines.append(f"<b>⭐ ({i}) <a href='{link}'>{fname}</a></b>")

        lines.append("\n<b>💡 Stay updated & never miss your favorite content!</b>")
        lines.append("<b><blockquote>Powered by - <a href='https://t.me/Ans_Links'>AnS Links 🔗</a></blockquote></b>")

        full_text = "\n".join(lines)

        # Split into chunks if needed
        chunks = split_text(full_text)
        total_pages = len(chunks)

        # Button for last message
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/YourAdminUsername")]
        ])

        for page_num, chunk in enumerate(chunks, 1):
            if total_pages > 1:
                chunk += f"\n\n<b>📄 Page {page_num}/{total_pages}</b>"

            if page_num == total_pages:
                # Last chunk with button & pin
                last_msg = await client.send_message(
                    chat_id=CHANNEL_ID,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                    reply_markup=buttons
                )
                logging.info("✅ Sent last chunk with button")
                await client.pin_chat_message(CHANNEL_ID, last_msg.id, disable_notification=True)
                logging.info("📌 Last message pinned")

                # Delete pin notification
                await asyncio.sleep(1)
                try:
                    await client.delete_messages(CHANNEL_ID, last_msg.id + 1)
                    logging.info("🗑️ Pin notification deleted")
                except Exception as e:
                    logging.warning(f"⚠️ Could not delete pin notification: {e}")
            else:
                await client.send_message(
                    chat_id=CHANNEL_ID,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                logging.info("✅ Sent a chunk of the update")
TechVJUser: Client | None = None

class Bot(Client):
    def __init__(self):
        logging.info("🔹 Initializing Bot instance...")
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=1000,
            plugins={"root": "plugins"},
            sleep_threshold=10,
            max_concurrent_transmissions=6
        )
        self._user_session_started = False
        logging.info("✅ Bot instance initialized")

    async def _maybe_start_user_session(self):
        global TechVJUser
        if STRING_SESSION and LOGIN_SYSTEM == False:
            logging.info("🔑 STRING_SESSION found, starting TechVJUser...")
            try:
                TechVJUser = Client(
                    "TechVJUser",
                    api_id=API_ID,
                    api_hash=API_HASH,
                    session_string=STRING_SESSION
                )
                await TechVJUser.start()
                self._user_session_started = True
                me = await TechVJUser.get_me()
                logging.info(f"✅ TechVJUser started: {me.first_name} (@{getattr(me, 'username', 'no-username')})")
            except Exception as e:
                logging.error(f"❌ Failed to start TechVJUser: {e}")
                TechVJUser = None
        else:
            logging.info("ℹ️ No STRING_SESSION or LOGIN_SYSTEM enabled, skipping user session startup")

    async def _maybe_stop_user_session(self):
        global TechVJUser
        if TechVJUser and self._user_session_started:
            logging.info("🛑 Stopping TechVJUser session...")
            try:
                await TechVJUser.stop()
                logging.info("✅ TechVJUser stopped")
            except Exception as e:
                logging.error(f"❌ Error stopping TechVJUser: {e}")
            finally:
                TechVJUser = None
                self._user_session_started = False

    async def start(self):
        logging.info("🚀 Starting Bot...")
        await self._maybe_start_user_session()

        logging.info("🔹 Starting Bot client...")
        await super().start()
        me = await self.get_me()
        logging.info(f"🤖 Bot running: {me.first_name} (@{me.username}) | Pyrogram v{__version__} Layer {layer}")

        try:
            tz = pytz.timezone('Asia/Kolkata')
            today = date.today()
            now = datetime.now(tz)
            time = now.strftime("%H:%M:%S %p")
            await self.send_message(7298944577, f"✅ Bot Restarted! 📅 {today} 🕒 {time}")
            logging.info("✅ Restart log sent to LOG_CHANNEL")
        except Exception as e:
            logging.error(f"❌ Could not send restart message to LOG_CHANNEL: {e}")

        try:
            logging.info("🌐 Starting web server...")
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            logging.info(f"🌐 Web server running on PORT {PORT}")

            # Start nightly update in background
            asyncio.create_task(nightly_update(self))

        except Exception as e:
            logging.error(f"❌ Failed to start web server: {e}")

    async def stop(self, *args):
        logging.info("🛑 Stopping Bot...")
        await self._maybe_stop_user_session()
        await super().stop()
        logging.info("🛑 Bot Stopped")

# Entry point
if __name__ == "__main__":
    logging.info("💡 Main execution started")
    try:
        app = Bot()
        app.run()
    except Exception as e:
        logging.error(f"❌ Bot crashed: {e}")
        logging.error("Traceback:\n" + "".join(logging.TracebackException.from_exception(e).format()))
