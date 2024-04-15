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


class TempRecord(BaseModel):
    """
    Record that is being kept in the in-memory ExpiringDict while being completed.
    Differs from the database Record in that it holds data on the Metrics that are being gathered.
    """

    metrics: list[Metric]
    data: dict[str, int | None] = {}
    timestamp: datetime = datetime.now()

    def __init__(self, **data):
        super().__init__(**data)
        self.data = {metric.name: None for metric in self.metrics}

    def update_data(self, metric_name: str, value: int):
        if metric_name in self.data:
            self.data[metric_name] = value
        else:
            raise ValueError(f"Metric {metric_name} not found in record data.")

    def next_unanswered_metric(self) -> Metric:
        return next(metric for metric in self.metrics if self.data[metric.name] is None)

    def is_complete(self) -> bool:
        return all(value is not None for value in self.data.values())
