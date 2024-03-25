from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    metrics: list[dict]
    notifications: list[str]
