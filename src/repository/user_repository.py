from pymongo import MongoClient

from src.autowiring.inject import autowire
from src.autowiring.injectable import Injectable
from src.config.config import Configuration
from src.model.metric import Metric
from src.model.notification import Notification
from src.model.user import User


class UserRepository(Injectable):
    def __init__(self, mongo_client: MongoClient):
        mood_tracker = mongo_client["mood_tracker"]
        self.user = mood_tracker["user"]

    def find_user(self, user_id: int) -> User | None:
        result = self.user.find_one({"user_id": user_id})
        if result:
            return self.parse_user(dict(result))
        return None

    def parse_user(self, result: dict) -> User:
        result = dict(result)
        # still not perfect from a typing point of view, but the hack is limited to the persistence layer
        result["notifications"] = [
            Notification(**notification) for notification in result["notifications"]
        ]
        return User(**result)

    @autowire("configuration")
    def create_user(self, user_id: int, configuration: Configuration) -> None:
        metrics = [metric.model_dump() for metric in configuration.get_metrics()]
        notifications = [
            notification.model_dump()
            for notification in configuration.get_notifications()
        ]
        auto_baseline_config = configuration.get_auto_baseline_config().model_dump()
        user_dict = {
            "user_id": user_id,
            "metrics": metrics,
            "notifications": notifications,
            "auto_baseline_config": auto_baseline_config,
        }
        self.user.insert_one(user_dict)
        return User(**user_dict)

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

    def update_user_metrics(self, user_id: int, metrics: list[Metric]) -> None:
        self.user.update_one(
            {"user_id": user_id},
            {"$set": {"metrics": [metric.model_dump() for metric in metrics]}},
        )

    def update_user_notifications(
        self, user_id: int, notifications: list[Notification]
    ) -> None:
        self.user.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "notifications": [
                        notification.model_dump() for notification in notifications
                    ]
                }
            },
        )

    def find_all_users(self) -> list[User]:
        return [self.parse_user(dict(u)) for u in self.user.find()]
