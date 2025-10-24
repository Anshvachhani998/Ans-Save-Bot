import logging
import logging.config
import os
import asyncio
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from aiohttp import web
import pytz
from datetime import date, datetime
from plugins import web_server
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL, PORT

try:
    from info import STRING_SESSION, LOGIN_SYSTEM
except Exception:
    STRING_SESSION = None
    LOGIN_SYSTEM = False

from pyrogram import types
from pyrogram import utils as pyroutils
from database.db import db
from asyncio import sleep

# adjust pyrogram minimum ids if needed
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

# Logging
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

import asyncio
from datetime import datetime, timedelta
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


CHANNEL_ID = -1003165005860

async def nightly_update():
    while True:
        now = datetime.now()
        # Calculate seconds until next midnight
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        wait_seconds = (next_midnight - now).total_seconds()
        wait_second = 60
        await asyncio.sleep(wait_second)

        # Fetch files added today
        all_users = await db.get_all_users()  # Your method to get all user_ids
        combined_movies = []
        combined_series = []

        for user_id in all_users:
            movies, series = await db.get_todays_files(user_id)
            combined_movies.extend(movies)
            combined_series.extend(series)

        if not combined_movies and not combined_series:
            continue  # Nothing to send

        # Prepare text with splitting if too long
        text = f"<b>📢 Daily Update\n📅 Date: {datetime.now().strftime('%d-%m-%Y')}\n🗃️ Total Files: {len(combined_movies)+len(combined_series)}\n\n"
        if combined_movies:
            text += "🍿 Movies\n"
            for i, m in enumerate(combined_movies, 1):
                match = re.match(r"(.+) \((.+)\)", m)
                if match:
                    fname, link = match.groups()
                    text += f"({i}) <a href='{link}'>{fname}</a>\n"
        if combined_series:
            text += "\n📺 Series\n"
            for i, s in enumerate(combined_series, 1):
                match = re.match(r"(.+) \((.+)\)", s)
                if match:
                    fname, link = match.groups()
                    text += f"({i}) <a href='{link}'>{fname}</a>\n"

        text += f"\n<blockquote>Powered by - <a href='https://t.me/Ans_Links'>AnS Links 🔗</a></blockquote></b>"

        # Split text if > 4000 chars
        chunks = split_text(text)

        # Button for pin chunk
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Contact Admin", url="https://t.me/YourAdminUsername")]
        ])

        # Send all chunks normally except last chunk
        for chunk in chunks[:-1]:
            await client.send_message(
                chat_id=CHANNEL_ID,
                text=chunk,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

        # Send last chunk, pin it
        last_chunk = chunks[-1]
        last_msg = await client.send_message(
            chat_id=CHANNEL_ID,
            text=last_chunk,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=buttons
        )
        await client.pin_chat_message(CHANNEL_ID, last_msg.message_id, disable_notification=True)

        # Delete pin notification (assume it comes immediately after pinned msg)
        import asyncio
        await asyncio.sleep(1)  # wait a second for notification to appear
        try:
            await client.delete_messages(CHANNEL_ID, last_msg.message_id + 1)
        except:
            pass


# Global user client reference
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
            asyncio.create_task(nightly_update())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            logging.info(f"🌐 Web server running on PORT {PORT}")
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
