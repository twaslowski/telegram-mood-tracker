import json

import boto3
from pyautowire import autowire

from src.config.config import Configuration
from src.model.user import User
from src.repository.user_repository import UserRepository


class DynamoDBUserRepository(UserRepository):
    def __init__(self, dynamodb: boto3.resource):
        self.table = dynamodb.Table("user")
        self.table.load()

    @autowire("configuration")
    def create_user(self, user_id: int, configuration: Configuration) -> User:
        user = User.from_defaults(user_id, configuration)
        self.table.put_item(Item=self.serialize_user(user))
        return user

    def find_user(self, user_id: int) -> User | None:
        result = self.table.get_item(Key={"user_id": user_id})
        user = result.get("Item")
        if user is not None:
            return self.parse_user(user)
        return None

    def update_user(self, user: User) -> None:
        # Technically, there's no such concept in DynamoDB. We can only put_item or delete_item.
        self.table.put_item(Item=self.serialize_user(user))

    def find_all_users(self) -> list[User]:
        response = self.table.scan()
        return [self.parse_user(item) for item in response["Items"]]

    @staticmethod
    def parse_user(result: dict) -> User:
        result["metrics"] = json.loads(result.get("metrics", "[]"))
        return User(**result)

    @staticmethod
    def serialize_user(user: User) -> dict:
        user_serialized = user.serialize()
        # DynamoDB does not maintain order in Maps, so the metrics get stringified to maintain order
        user_serialized["metrics"] = json.dumps(user_serialized["metrics"])
        return user_serialized
