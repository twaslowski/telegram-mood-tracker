import datetime
import os

import pymongo
from dotenv import load_dotenv

# use bracket notation over .get() to fail explicitly if environment variable is not supplied
mongo_url = os.getenv("MONGODB_HOST", "localhost:27017")
mongo_client = pymongo.MongoClient(f'mongodb://{mongo_url}/')
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]


def find_oldest_record_for_user(user_id: int) -> dict:
    return records.find_one(
        {"user_id": user_id}, sort=[("timestamp", pymongo.ASCENDING)]
    )


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def create_record(user_id: int, record: dict, timestamp: str):
    records.insert_one({"user_id": user_id, "record": record, "timestamp": timestamp})


def find_records_for_user(user_id: int) -> list:
    r = list(records.find({"user_id": user_id}))
    # map timestamps
    for record in r:
        record["timestamp"] = datetime.datetime.fromisoformat(record["timestamp"])
    return r


def zeroes(days: int):
    """
    Inserts records with default values for missed days within a date range.
    start_date (datetime.date): The start date of the range.
    end_date (datetime.date): The end date of the range.
    """

    user_id = 1965256751
    default_record = {"sleep": "8", "mood": "0"}
    start = datetime.datetime.now().isoformat()
    date_range = [modify_timestamp(start, n).isoformat() for n in range(days)]

    for date in date_range:
        print(f"Inserting neutral record for timestamp {date}")
        create_record(user_id, default_record, date)


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
