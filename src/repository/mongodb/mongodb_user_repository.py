import logging

from pymongo import MongoClient

from pyautowire import autowire
from src.config.config import Configuration
from src.model.user import User
from src.repository.user_repository import UserRepository


class MongoDBUserRepository(UserRepository):
    def __init__(self, mongo_client: MongoClient):
        super().__init__()
        mood_tracker = mongo_client["mood_tracker"]
        self.user = mood_tracker["user"]
        logging.info("MongoDBUserRepository initialized.")

    def find_user(self, user_id: int) -> User | None:
        result = self.user.find_one({"user_id": user_id})
        logging.info(f"Found user: {result}")
        if result:
            return self.parse_user(dict(result))
        return None

    @staticmethod
    def parse_user(result: dict) -> User:
        return User(**result)

    @autowire("configuration")
    def create_user(self, user_id: int, configuration: Configuration) -> User:
        user = User.from_defaults(user_id, configuration)
        self.user.insert_one(user.serialize())
        return user

    def update_user(self, user: User) -> None:
        self.user.update_one(
            {"user_id": user.user_id},
            {
                "$set": {
                    "metrics": [metric.model_dump() for metric in user.metrics],
                    "notifications": [
                        notification.model_dump() for notification in user.notifications
                    ],
                    "auto_baseline_config": user.auto_baseline_config.model_dump(),
                }
            },
        )

    def find_all_users(self) -> list[User]:
        return [self.parse_user(dict(u)) for u in self.user.find()]
