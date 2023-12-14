import datetime
import os

import pymongo
from dotenv import load_dotenv

from src import config

load_dotenv()

mongo_url = f"mongodb://{os.environ.get('MONGO_CONNECTION_STRING')}/"
mongo_client = pymongo.MongoClient(mongo_url)
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]
user = mood_tracker["user"]


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def find_user(user_id: int) -> dict:
    return user.find_one({"user_id": user_id})


def create_user(user_id: int) -> None:
    user.insert_one({
        "user_id": user_id,
        "metrics": config.defaults.get('metrics'),
        "notifications": config.defaults.get('notifications')
    })


def find_oldest_record_for_user(user_id: int) -> dict:
    return records.find_one({"user_id": user_id}, sort=[("timestamp", pymongo.ASCENDING)])


def get_all_user_notifications() -> dict:
    """
    Returns dict of user_id to their respective notification times
    :return: dict of user_id: [notification_time]
    """
    return {u['user_id']: [datetime.time.fromisoformat(t) for t in u['notifications']] for u in user.find()}


def get_user_config(user_id: int) -> dict:
    return user.find_one({'user_id': user_id})['metrics']


def delete_all() -> None:
    records.delete_many({})


def create_record(user_id: int, record: dict, timestamp: str):
    records.insert_one({"user_id": user_id, "record": record, "timestamp": timestamp})


def find_records_for_user(user_id: int) -> list:
    r = list(records.find({"user_id": user_id}))
    # map timestamps
    for record in r:
        record['timestamp'] = datetime.datetime.fromisoformat(record['timestamp'])
    return r
