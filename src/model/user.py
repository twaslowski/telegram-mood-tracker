from pydantic import BaseModel

from src.model.metric import Metric
from src.model.notification import Notification


class User(BaseModel):
    user_id: int
    metrics: list[Metric]
    notifications: list[Notification]
    auto_baseline: bool = False

    def has_baselines_defined(self) -> bool:
        return all(metric.baseline is not None for metric in self.metrics)
