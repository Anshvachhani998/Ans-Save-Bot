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
            await self.send_message(LOG_CHANNEL, f"✅ Bot Restarted! 📅 {today} 🕒 {time}")
            logging.info("✅ Restart log sent to LOG_CHANNEL")
        except Exception as e:
            logging.error(f"❌ Could not send restart message to LOG_CHANNEL: {e}")

        try:
            logging.info("🌐 Starting web server...")
            app = web.AppRunner(await web_server())
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
