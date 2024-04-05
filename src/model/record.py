from datetime import datetime

from pydantic import BaseModel

from src.model.metric import Metric


class RecordData(BaseModel):
    """
    Represents an instance of a metric, i.e. the metric name and a corresponding value.
    """

    metric_name: str
    value: int | None


class DatabaseRecord(BaseModel):
    """
    This exists for backwards-compatibility, as an abstraction layer to deal with my previous bad decisions.
    It wraps the existing database record structure and allows me to build on top of it with relative ease.
    """

    _id: str
    user_id: int
    record: dict[str, int]
    timestamp: str  # iso-formatted

    def to_record(self) -> "Record":
        return Record(
            user_id=self.user_id,
            data=[RecordData(metric_name=k, value=v) for k, v in self.record.items()],
            timestamp=datetime.fromisoformat(self.timestamp),
        )


class AbstractRecord(BaseModel):
    """
    Can provide shared methods for Record and TempRecord.
    """

    def find_record_data_by_name(self, name: str) -> RecordData | None:
        return next((x for x in self.data if x.metric_name == name), None)

    def find_metric_by_name(self, name: str) -> Metric | None:
        return next((x for x in self.metrics if x.name == name), None)


class Record(AbstractRecord):
    user_id: int
    data: list[RecordData]
    timestamp: datetime


class TempRecord(AbstractRecord):
    """
    Record that are kept in the in-memory ExpiringDict while being completed.
    """

    metrics: list[Metric]
    data: list[RecordData] = None  # initialised in __init__
    timestamp: datetime = datetime.now()

    # todo test
    def update_data(self, name: str, value: int | None):
        record_data = self.find_record_data_by_name(name)
        if record_data:
            record_data.value = value
        else:
            raise ValueError(f"Metric {name} not found in record data.")

    def is_complete(self) -> bool:
        return all([x.value is not None for x in self.data])

    def __init__(self, **data):
        super().__init__(**data)
        self.data = [
            RecordData(metric_name=metric.name, value=None) for metric in self.metrics
        ]
