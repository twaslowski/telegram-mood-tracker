from pyautowire import autowire

from src.service.user_service import UserService


@autowire("user_service")
def stats_handler(user_service: UserService):
    pass
