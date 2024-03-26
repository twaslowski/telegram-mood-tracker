import os

import pymongo
from src.model.notification import Notification
from src.model.user import User
from src import config

mongo_url = os.getenv("MONGODB_HOST", "localhost:27017")
mongo_client = pymongo.MongoClient(mongo_url)
mood_tracker = mongo_client["mood_tracker"]
user = mood_tracker["user"]


def find_user(user_id: int) -> User | None:
    result = user.find_one({"user_id": user_id})
    if result:
        return parse_user(dict(result))
    return None


def parse_user(result: dict) -> User:
    result = dict(result)
    # still not perfect from a typing point of view, but the hack is limited to the persistence layer
    result["notifications"] = [
        Notification(**notification) for notification in result["notifications"]
    ]
    return User(**result)


def create_user(user_id: int) -> None:
    user.insert_one(
        {
            "user_id": user_id,
            "metrics": [metric.model_dump() for metric in config.default_metrics()],
            "notifications": [
                notification.model_dump()
                for notification in config.default_notifications()
            ],
        }
    )


def find_all_users() -> list[User]:
    return [parse_user(dict(u)) for u in user.find()]
