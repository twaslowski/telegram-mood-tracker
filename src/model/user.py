from pydantic import BaseModel

from src.model.notification import Notification


class User(BaseModel):
    user_id: int
    metrics: list[dict]
    notifications: list[Notification]
