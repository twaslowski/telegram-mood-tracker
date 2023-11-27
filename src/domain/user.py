from src import config


class User:
    user_id: int
    metrics: dict
    notifications: list

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.metrics = config.defaults['metrics']
        self.notifications = config.defaults['notifications']
