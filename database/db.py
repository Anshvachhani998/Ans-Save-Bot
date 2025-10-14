import motor.motor_asyncio
from info import DB_NAME, DB_URI
from datetime import datetime, timedelta


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db["newusers"]


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
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
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

db = Database(DB_URI, DB_NAME)
