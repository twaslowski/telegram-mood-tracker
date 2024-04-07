import boto3
from pyautowire import autowire, Injectable

from src.config.config import Configuration
from src.model.user import User


class DynamoDBUserRepository(Injectable):
    def __init__(self):
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        self.table = dynamodb.Table("user")
        self.table.load()

    @autowire("configuration")
    def create_user(self, user_id: int, configuration: Configuration) -> User:
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
        self.table.put_item(Item=user_dict)
        return User(**user_dict)

    def find_user(self, user_id: int) -> User | None:
        result = self.table.get_item(Key={"user_id": user_id})
        if result:
            return self.parse_user(result["Item"])
        return None

    @staticmethod
    def parse_user(result: dict) -> User:
        return User(**result)

    def update_user(self, user: User) -> None:
        # Technically, there's no such concept in DynamoDB. We can only put_item or delete_item.
        self.table.update_one(
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
        response = self.table.scan()
        return [self.parse_user(item) for item in response["Items"]]
