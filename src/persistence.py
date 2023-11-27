import datetime

import pymongo

import src.config as config
from src.domain.user import User

mongo_url = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_url)
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]
user = mood_tracker["user"]


def save_record(record: dict) -> None:
    records.insert_one(record)


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def update_latest_record(record: dict) -> None:
    latest = get_latest_record()
    latest.update(record)
    records.replace_one({"_id": latest["_id"]}, latest)


def find_user(user_id: int) -> dict:
    return user.find_one({"user_id": user_id})


def create_user(u: User) -> None:
    user.insert_one({
        "user_id": u.user_id,
        "metrics": u.metrics,
        "notifications": u.notifications
    })


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


def create_record(user_id: int, record: dict):
    records.insert_one({"user_id": user_id, "record": record})


def find_records_for_user(user_id: int) -> list:
    return list(records.find({"user_id": user_id}))
