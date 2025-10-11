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

# Try to import optional settings (STRING_SESSION, LOGIN_SYSTEM). Use safe defaults if missing.
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
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Global user client reference
TechVJUser: Client | None = None

class Bot(Client):
    def __init__(self):
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
        # Keep track whether user session was started here
        self._user_session_started = False

    async def _maybe_start_user_session(self):
        """
        Start TechVJUser if STRING_SESSION is provided and LOGIN_SYSTEM is False.
        This runs before bot start so the user client is available during bot runtime.
        """
        global TechVJUser
        if STRING_SESSION and LOGIN_SYSTEM == False:
            try:
                logging.info("🔑 STRING_SESSION found — starting TechVJUser session...")
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
            logging.info("ℹ️ No STRING_SESSION provided or LOGIN_SYSTEM enabled — skipping user session startup.")

    async def _maybe_stop_user_session(self):
        """
        Stop the TechVJUser if it was started by this process.
        """
        global TechVJUser
        if TechVJUser and self._user_session_started:
            try:
                logging.info("🛑 Stopping TechVJUser session...")
                await TechVJUser.stop()
                logging.info("✅ TechVJUser stopped.")
            except Exception as e:
                logging.error(f"❌ Error stopping TechVJUser: {e}")
            finally:
                TechVJUser = None
                self._user_session_started = False

    async def start(self):
        # Start user session first (if applicable)
        await self._maybe_start_user_session()

        # Then start the bot client
        await super().start()
        me = await self.get_me()
        logging.info(f"🤖 {me.first_name} (@{me.username}) running on Pyrogram v{__version__} (Layer {layer})")

        # Send restart log to configured channel (if available)
        try:
            tz = pytz.timezone('Asia/Kolkata')
            today = date.today()
            now = datetime.now(tz)
            time = now.strftime("%H:%M:%S %p")
            await self.send_message(chat_id=LOG_CHANNEL, text=f"✅ Bot Restarted! 📅 Date: {today} 🕒 Time: {time}")
        except Exception as e:
            logging.error(f"Could not send restart message to LOG_CHANNEL: {e}")

        # Start web server (plugin-provided)
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", PORT).start()
            logging.info(f"🌐 Web Server Running on PORT {PORT}")
        except Exception as e:
            logging.error(f"Failed to start web server: {e}")

    async def stop(self, *args):
        # Stop user session first (if started)
        await self._maybe_stop_user_session()

        # Then stop the bot
        await super().stop()
        logging.info("🛑 Bot Stopped.")

# Entry point
if __name__ == "__main__":
    logging.info("🚀 Starting Bot (with optional TechVJUser session)...")
    app = Bot()
    app.run()
