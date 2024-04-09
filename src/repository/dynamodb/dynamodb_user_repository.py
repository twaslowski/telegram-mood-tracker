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
        self.table.put_item(Item=user.dict())
        return user

    def find_user(self, user_id: int) -> User | None:
        result = self.table.get_item(Key={"user_id": user_id})
        user = result.get("Item")
        if user is not None:
            return self.parse_user(user)
        return None

    def update_user(self, user: User) -> None:
        # Technically, there's no such concept in DynamoDB. We can only put_item or delete_item.
        self.table.put_item(Item=user.dict())

    def find_all_users(self) -> list[User]:
        response = self.table.scan()
        return [self.parse_user(item) for item in response["Items"]]
