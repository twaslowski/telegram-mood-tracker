import datetime
import os

import pymongo
from dotenv import load_dotenv

from src import config
from src.model.user import User

load_dotenv()

# use bracket notation over .get() to fail explicitly if environment variable is not supplied
mongo_url = f"mongodb://{os.environ['MONGO_CONNECTION_STRING']}/"
mongo_client = pymongo.MongoClient(mongo_url)
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]
user = mood_tracker["user"]


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def find_user(user_id: int) -> User | None:
    result = user.find_one({"user_id": user_id})
    if result:
        return User(**result)
    return None


def create_user(user_id: int) -> None:
    user.insert_one(
        {
            "user_id": user_id,
            "metrics": config.defaults.get("metrics"),
            "notifications": config.defaults.get("notifications"),
        }
    )


def find_oldest_record_for_user(user_id: int) -> dict:
    return records.find_one(
        {"user_id": user_id}, sort=[("timestamp", pymongo.ASCENDING)]
    )


def get_all_user_notifications() -> dict:
    """
    Returns dict of user_id to their respective notification times
    :return: dict of user_id: [notification_time]
    """
    return {
        u["user_id"]: [datetime.time.fromisoformat(t) for t in u["notifications"]]
        for u in user.find()
    }


def delete_all() -> None:
    records.delete_many({})


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


def migrate() -> None:
    """
    Migrate from old format to new format
    """
    old_db = mongo_client["records"]
    new_db = mongo_client["mood_tracker"]

    # Select your collection
    old_collection = old_db.records
    new_collection = new_db.records

    for doc in old_collection.find():
        new_doc = {
            "user_id": os.environ["CHAT_ID"],  # my own personal chat id
            "timestamp": doc["timestamp"],
            "record": doc["record"],
        }
        new_collection.insert_one(new_doc)

    print("Migration completed.")

    # Close the MongoDB connection
    mongo_client.close()


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)


if __name__ == "__main__":
    zeroes(17)
