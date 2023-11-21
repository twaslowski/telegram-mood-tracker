import pymongo

mongo_url = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_url)
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]
user = mood_tracker["user"]

import src.config as config


def save_record(record: dict) -> None:
    records.insert_one(record)


def list_records() -> list:
    return list(records.find({}))


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def update_latest_record(record: dict) -> None:
    latest = get_latest_record()
    latest.update(record)
    records.replace_one({"_id": latest["_id"]}, latest)


def delete_latest_record():
    latest = get_latest_record()
    records.delete_one({"_id": latest["_id"]})


def find_user(user_id: int) -> dict:
    return user.find_one({"user_id": user_id})


def create_user(user_id: int) -> None:
    user.insert_one(
        {"user_id": user_id, "metrics": config.config['metrics'], "notifications": config.config['notifications']})


def delete_all() -> None:
    records.delete_many({})
