from pydantic import BaseModel

from src.model.metric import Metric
from src.model.notification import Notification


class User(BaseModel):
    user_id: int
    metrics: list[Metric]
    notifications: list[Notification]

    def has_baselines_defined(self):
        return all(metric.baseline for metric in self.metrics)
