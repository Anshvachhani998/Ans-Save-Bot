

import os
LOGIN_SYSTEM = os.environ.get('LOGIN_SYSTEM', 'True').lower() == 'true'

STRING_SESSION = ""


if LOGIN_SYSTEM == False:
    # if login system is false then fill your tg account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "")

ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))

DB_URI = os.environ.get("DB_URI", "mongodb+srv://Ansh089:Ansh089@cluster0.y8tpouc.mongodb.net/?retryWrites=true&w=majority")
DB_NAME = os.environ.get("DB_NAME", "YouTubeDL")


SESSION = "savebot"
API_ID = int(os.getenv("API_ID", "29256205"))
API_HASH = os.getenv("API_HASH", "0c4124e19f592dc4290c035f4814b9b9")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7985040786:AAH11LYIfSN8KIpWHYNC-88T63_8w4PBCG4")
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003108208332"))
DUMP_CHANNEL_ID = int(os.getenv("DUMP_CHANNEL_ID", "-1002890289206"))
JIO_DUMP = int(os.getenv("JIO_DUMP", "-1003022720180"))
PORT = int(os.getenv("PORT", "8084"))
FORCE_CHANNEL = int(os.getenv("FORCE_CHANNEL", "-1002849184248"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Ansh089:Ansh089@cluster0.y8tpouc.mongodb.net/?retryWrites=true&w=majority")
MONGO_NAME = os.getenv("MONGO_NAME", "jsut")

MONGO_URI_2 = os.getenv("MONGO_URI_2", "mongodb+srv://ftmbotzx:ftmbotzx@cluster0.0b8imks.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
MONGO_NAME_2 = os.getenv("MONGO_NAME_2", "just")

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "just")
ADMINS = [5660839376, 6167872503, 5961011848, 6538627123, 8104777494, 7298944577]
OWNER_ID = 7744665378
DAILY_LIMITS = 20
MAINTENANCE_MODE = False
USER_SESSION = "BQG-ag0APB80-3ZZdcruJrsSxQUwM0rIPGUZERFu5K210FAr7VDYQfBzZNsuRNGfLCuDX_yU1dYWhHnnnfj15YUp2GGlNXciBN3-_W_mex74ELog9YDhTcNBkwrN0xZrh8A2RCg9-MkYdL2_TVF3cqQQXwA2BeZkN8qMyZl5KJVed5OR2rsv9eJFqmKcVrTN6jhbGqwDuXOeFZrKZg1avGw4NNoaUcsJ8a8iJ3_TtmjKYurZpgFzjd8X1yPcUyX3LOty8XqbyYh8TBpQXJpoLCiXfJzaqaTdQix9S8lpFCXJYswvUk6J-f2x-Kq-KHV_yX0OZD7n5a6SaLLnHQ1n4KGegCTSIAAAAAHNx1kMAA"
USERBOT_CHAT_ID = 5785483456
FAILD_CHAT_ID = int(os.getenv("FAILD_CHAT_ID", "-1002849184248"))
GROUP_ID = [-1002526173846, -1002508944571, -1002713034219]
REQ_CHANNEL = -1003186496490

MAX_PLAYLIST = 500
USE_SPOTIFY_API = True
DELETE_CHANNELS = -1003036780293
MAINTENANCE_MESSAGE = (
    "⚠️ **Maintenance Mode Activated** ⚙️\n\n"
    "Our bot is currently undergoing scheduled maintenance to improve performance and add new features.\n\n"
    "Please check back in a while. We’ll be back soon, better than ever!\n\n"
    "💬 **Support Group:** [SUPPORT](https://t.me/AnSBotsSupports)\n\n"
    "**– Team Support**"
)


FORCE_SUB_MODE = False  # ✅ Enable/Disable force join
FORCE_JOIN = "AnsMusicHQ"
