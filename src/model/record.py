from datetime import datetime

from pydantic import BaseModel

from src.model.metric import Metric


class Record(BaseModel):
    """
    Record model that is stored in the database.
    """

    user_id: int
    data: dict[str, int]
    timestamp: datetime

    def serialize(self):
        return {
            "user_id": self.user_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self):
        return f"user_id: {self.user_id}, data: {self.data}, timestamp: {self.timestamp.isoformat()}"


class TempRecord:
    """
    Record that is being kept in the in-memory ExpiringDict while being completed.
    Differs from the database Record in that it holds data on the Metrics that are being gathered.
    """

    metrics: list[Metric]
    timestamp: datetime
    data: dict[str, int | None]

    def __init__(self, metrics: list[Metric]):
        self.metrics = metrics
        self.data = {metric.name: None for metric in self.metrics}
        self.timestamp = datetime.now()

    def __str__(self):
        return f"data: {self.data}, timestamp: {self.timestamp.isoformat()}"

    def update_data(self, metric_name: str, value: int):
        if metric_name in self.data:
            self.data[metric_name] = value
        else:
            raise ValueError(f"Metric {metric_name} not found in record data.")

    def next_unanswered_metric(self) -> Metric:
        return next(metric for metric in self.metrics if self.data[metric.name] is None)

    def is_complete(self) -> bool:
        return all(value is not None for value in self.data.values())
