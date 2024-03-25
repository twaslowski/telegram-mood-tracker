import datetime

from pydantic import BaseModel


class Notification(BaseModel):
    time: datetime.datetime
    text: str
