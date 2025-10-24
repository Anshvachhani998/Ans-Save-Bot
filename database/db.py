import motor.motor_asyncio
from info import DB_NAME, DB_URI
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import re

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.db = self.client[DB_NAME]
        self.col = self.db["newusers"]
        self.downloads_collection = self.db["downloads"]
        self.mydb = mydb = self.db["filename"]


    def new_user(self, id, name):
        return {
            "user_id": int(id),
            "name": name,
            "joined_at": datetime.utcnow(),
            "user_type": "free",
            "tasks_used": 0,
            "total_tasks": 0,
            "last_reset": datetime.utcnow().strftime("%Y-%m-%d")
        }

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)


    async def get_todays_files(self, user_id, date_str: str = None):
        """
        Fetch movies and series added on a given date for a specific user.
        If date_str is None, fetch today's files by default.

        Args:
            user_id (int): Telegram user ID
            date_str (str, optional): Date in "YYYY-MM-DD" format. Defaults to None.

        Returns:
            tuple: (movies, series) lists
        """
        user_db = self.mydb[str(user_id)]
        
        # Use provided date or default to today
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")

        cursor = user_db.find({"date": date_str})
        movies = []
        series = []

        async for doc in cursor:
            filename = doc['_id']
            link = f"https://t.me/c/2181749207/{doc['msg_id']}"  # your link format
            entry = f"{filename} ({link})"
            
            if re.search(r"S\d{2}", filename, re.IGNORECASE):
                series.append(entry)
            else:
                movies.append(entry)

        return movies, series
        
    async def is_filename_present(self, filename, user_id):
        """
        Check if filename is present in the database.
        """
        user_db = self.mydb[str(user_id)]
        result = await user_db.count_documents({"_id": filename})
        return result > 0

    async def add_name(self, user_id, filename, msg_id):
        """
        Add a filename along with message ID, file name, and timestamp to the DB.
        """
        user_db = self.mydb[str(user_id)]

        # Check if the filename already exists
        existing_user = await user_db.find_one({'_id': filename})
        if existing_user is not None:
            return False

        now = datetime.now()
        user_entry = {
            "_id": filename,
            "msg_id": msg_id,
            "date": now.strftime("%Y-%m-%d"),
        }

        try:
            await user_db.insert_one(user_entry)
            return True
        except DuplicateKeyError:
            return False
            

    async def is_user_exist(self, id):
        user = await self.col.find_one({"user_id": int(id)})
        return bool(user)
        
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session')

db = Database()
