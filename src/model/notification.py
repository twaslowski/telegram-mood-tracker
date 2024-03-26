import datetime

from pydantic import BaseModel


class Notification(BaseModel):
    time: datetime.time
    text: str

    def model_dump(self, **kwargs):
        return {
            "time": self.time.isoformat(),
            "text": self.text,
            **kwargs,
        }
