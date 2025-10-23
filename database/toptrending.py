import pymongo
from info import DATABASE_NAME, DATABASE_URI
from datetime import datetime, timedelta
import pytz
from info import DB_URI, DB_NAME
import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError

import logging
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)



class Toptrending:
    def __init__(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        db = client[DB_NAME]
        self.forwarded_files = db["forwarded_files"]
        self.search_files = db["search_files"]
        self.totalverified = db["total_verified"]
        self.mydb = mydb = db["filename"]


        
    async def is_filename_present(self, filename):
        """
        Check if filename is present in the database.
        """
        user_id = 5660839376
        user_db = self.mydb[str(user_id)]  # Replace self.mydb with your database connection
        result = await user_db.count_documents({"_id": filename})
        return result > 0

    async def add_name(self, user_id, filename, message_id=None):
        """
        Add a filename for a user with date and chat_id.
        """
        user_db = self.mydb[str(user_id)]
        date = datetime.datetime.now().strftime("%d-%m-%Y")

        existing = await user_db.find_one({"_id": filename})
        if existing:
            return False

        entry = {
            "_id": filename,
            "date": date,
            "message_id": message_id
        }

        try:
            await user_db.insert_one(entry)
            return True
        except DuplicateKeyError:
            return False

    
    async def delete_all_msg(self, user_id):
        user_db = self.mydb[str(user_id)]
        user_db.delete_many({})

        
    async def add_forward(self, file_id, file_name):
        # Get current date and time
        current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))

        # Get current date
        current_date = datetime.combine(current_datetime.date(), datetime.min.time())

        # Extract current month, year, and day
        current_month = current_date.month
        current_year = current_date.year
        current_day = current_date.day

        # Check if the file exists in the collection
        existing_file = await self.forwarded_files.find_one({"file_id": file_id})

        if existing_file:
            last_forwarded_datetime = existing_file.get("last_forwarded")  # Get last forwarded datetime
            last_forwarded_date = datetime.combine(last_forwarded_datetime.date(), datetime.min.time())  # Convert to datetime object

            # Extract last forwarded month, year, and day
            last_forwarded_month = last_forwarded_date.month
            last_forwarded_year = last_forwarded_date.year
            last_forwarded_day = last_forwarded_date.day

            # Calculate the difference in months
            month_difference = (current_year - last_forwarded_year) * 12 + current_month - last_forwarded_month

            # Update counts for the current month, year, and total
            if current_month == last_forwarded_month and current_year == last_forwarded_year:
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$inc": {"this_month": 1, "this_year": 1, "total_count": 1}},
                    upsert=False
                )
            elif current_year == last_forwarded_year:
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$set": {"this_month": 1}, "$inc": {"this_year": 1, "total_count": 1}},
                    upsert=False
                )
            else:
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$set": {"this_month": 1, "this_year": 1}, "$inc": {"total_count": 1}},
                    upsert=False
                )

            # If the last forwarded date is the current date, update the forward count for today and the last forwarded date
            if last_forwarded_date.date() == current_date.date():
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$inc": {"forward_count_today": 1}, "$set": {"last_forwarded": current_date}},
                    upsert=False
                )
            elif (current_date - last_forwarded_date).days == 1:  # If there's a gap of 1 day
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$set": {
                        "forward_count_yesterday": existing_file.get("forward_count_today", 0),
                        "forward_count_today": 1,
                        "last_forwarded": current_date
                    }},
                    upsert=False
                )
            else:  # Reset today's count if there's a gap of more than 1 day
                await self.forwarded_files.update_one(
                    {"file_id": file_id},
                    {"$set": {
                        "forward_count_today": 1,
                        "forward_count_yesterday": 0,
                        "last_forwarded": current_date
                    }},
                    upsert=False
                )
        else:
            # If the file doesn't exist, add it to the collection with forward count for today
            await self.forwarded_files.insert_one(
                {
                    "file_id": file_id,
                    "file_name": file_name,
                    "forward_count_today": 1,
                    "forward_count_yesterday": 0,
                    "this_month": 1,
                    "this_year": 1,
                    "total_count": 1,
                    "last_forwarded": current_date
                }
                      )

    async def add_search_list(self, search):
        # Get current date and time
        current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))

        # Get current date
        current_date = datetime.combine(current_datetime.date(), datetime.min.time())

        # Extract current month, year, and day
        current_month = current_date.month
        current_year = current_date.year
        current_day = current_date.day

        # Check if the file exists in the collection
        existing_file = await self.search_files.find_one({"search": {"$regex": f'^{search}$', "$options": "i"}})

        if existing_file:
            last_forwarded_datetime = existing_file.get("last_forwarded")  # Get last forwarded datetime
            last_forwarded_date = datetime.combine(last_forwarded_datetime.date(), datetime.min.time())  # Convert to datetime object

            # Extract last forwarded month, year, and day
            last_forwarded_month = last_forwarded_date.month
            last_forwarded_year = last_forwarded_date.year
            last_forwarded_day = last_forwarded_date.day

            # Calculate the difference in months
            month_difference = (current_year - last_forwarded_year) * 12 + current_month - last_forwarded_month

            # Update counts for the current month, year, and total
            if current_month == last_forwarded_month and current_year == last_forwarded_year:
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$inc": {"this_month": 1, "this_year": 1, "total_count": 1}},
                    upsert=False
                )
            elif current_year == last_forwarded_year:
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$set": {"this_month": 1}, "$inc": {"this_year": 1, "total_count": 1}},
                    upsert=False
                )
            else:
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$set": {"this_month": 1, "this_year": 1}, "$inc": {"total_count": 1}},
                    upsert=False
                )

            # If the last forwarded date is the current date, update the forward count for today and the last forwarded date
            if last_forwarded_date.date() == current_date.date():
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$inc": {"search_count_today": 1}, "$set": {"last_forwarded": current_date}},
                    upsert=False
                )
            elif (current_date - last_forwarded_date).days == 1:  # If there's a gap of 1 day
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$set": {
                        "search_count_yesterday": existing_file.get("search_count_today", 0),
                        "search_count_today": 1,
                        "last_forwarded": current_date
                    }},
                    upsert=False
                )
            else:  # Reset today's count if there's a gap of more than 1 day
                await self.search_files.update_one(
                    {"search": {"$regex": f'^{search}$', "$options": "i"}},
                    {"$set": {
                        "search_count_today": 1,
                        "search_count_yesterday": 0,
                        "last_forwarded": current_date
                    }},
                    upsert=False
                )
        else:
            # If the file doesn't exist, add it to the collection with forward count for today
            await self.search_files.insert_one(
                {
                    "search": search,
                    "search_count_today": 1,
                    "search_count_yesterday": 0,
                    "this_month": 1,
                    "this_year": 1,
                    "total_count": 1,
                    "last_forwarded": current_date
                }
            )



    async def total_verified(self):
        # Get current date and time
        current_datetime = datetime.now(pytz.timezone("Asia/Kolkata"))

        # Get current date
        current_date = datetime.combine(current_datetime.date(), datetime.min.time())

        # Extract current month, year, and day
        current_month = current_date.month
        current_year = current_date.year
        current_day = current_date.day

        # Check if the file exists in the collection
        total_verified = await self.totalverified.find_one({"TOTAL_VERIFIED": "ANSH"})

        if total_verified:
            last_verified_datetime = total_verified.get("last_verified")  # Get last forwarded datetime
            last_verified_date = datetime.combine(last_verified_datetime.date(), datetime.min.time())  # Convert to datetime object

            # Extract last forwarded month, year, and day
            last_verified_month = last_verified_date.month
            last_verified_year = last_verified_date.year
            last_verified_day = last_verified_date.day

            # Calculate the difference in months
            month_difference = (current_year - last_verified_year) * 12 + current_month - last_verified_month

            # Update counts for the current month, year, and total
            if current_month == last_verified_month and current_year == last_verified_year:
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$inc": {"this_month": 1, "this_year": 1, "total_verified": 1}},
                    upsert=False
                )
            elif current_year == last_verified_year:
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$set": {"this_month": 1}, "$inc": {"this_year": 1, "total_verified": 1}},
                    upsert=False
                )
            else:
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$set": {"this_month": 1, "this_year": 1}, "$inc": {"total_verified": 1}},
                    upsert=False
                )

            # If the last forwarded date is the current date, update the forward count for today and the last forwarded date
            if last_verified_date.date() == current_date.date():
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$inc": {"verified_count_today": 1}, "$set": {"last_verified": current_date}},
                    upsert=False
                )
            elif (current_date - last_verified_date).days == 1:  # If there's a gap of 1 day
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$set": {
                        "verified_count_yesterday": total_verified.get("verified_count_today", 0),
                        "verified_count_today": 1,
                        "last_verified": current_date
                    }},
                    upsert=False
                )
            else:  # Reset today's count if there's a gap of more than 1 day
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$set": {
                        "verified_count_today": 1,
                        "verified_count_yesterday": 0,
                        "last_verified": current_date
                    }},
                    upsert=False
                )

            # Check if last month's count needs to be updated
            if month_difference == 1:
                # If there's a gap of 1 month, update last month's count
                await self.totalverified.update_one(
                    {"TOTAL_VERIFIED": "ANSH"},
                    {"$set": {"last_month_count": total_verified.get("this_month", 0)}},
                    upsert=False
                )            
        else:
            # If the file doesn't exist, add it to the collection with forward count for today
            await self.totalverified.insert_one(
                {
                    "TOTAL_VERIFIED": "ANSH", 
                    "verified_count_today": 1,
                    "verified_count_yesterday": 0,
                    "this_month": 1,
                    "last_month_count": 0,
                    "this_year": 1,
                    "total_verified": 1,
                    "last_verified": current_date
                }
            )
        
top = Toptrending()
