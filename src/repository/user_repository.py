from abc import ABC, abstractmethod

from pyautowire import Injectable

from src.config.config import Configuration
from src.model.user import User


class UserRepository(Injectable, ABC):
    @staticmethod
    def parse_user(result: dict) -> User:
        return User(**result)

    @abstractmethod
    def find_user(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def create_user(self, user_id: int, configuration: Configuration) -> User:
        pass

    @abstractmethod
    def update_user(self, user: User) -> None:
        pass

    @abstractmethod
    def find_all_users(self) -> list[User]:
        pass
