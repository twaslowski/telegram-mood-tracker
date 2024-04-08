from pyautowire import Injectable
from src.model.user import User


class UserRepository(Injectable):
    @staticmethod
    def parse_user(result: dict) -> User:
        return User(**result)
