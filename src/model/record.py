from datetime import datetime

from pydantic import BaseModel

from src.model.metric import Metric


class RecordData(BaseModel):
    """
    Represents an instance of a metric, i.e. the metric name and a corresponding value.
    """

    metric_name: str
    value: int | None


class Record(BaseModel):
    user_id: int
    data: dict[str, int]
    timestamp: datetime


class TempRecord(BaseModel):
    """
    Record that are kept in the in-memory ExpiringDict while being completed.
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
