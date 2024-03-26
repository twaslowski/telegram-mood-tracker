from datetime import datetime

from pydantic import BaseModel
from dataclasses import dataclass

from src.model.metric import Metric


class RecordData(BaseModel):
    # chosen like this for backward compatibility
    metric_name: str
    value: int | None


class Record(BaseModel):
    """
    Record that is kept in the database. Backwards-compatible with the existing scheme via model_dump().
    """

    user_id: int
    # this name is very unintuitive, as it overloads the meaning of the word "record"
    # it is chosen like this for backward compatibility,
    # but it should be migrated to something like 'data' or 'record_data' in the future
    record: list[RecordData]
    # gets serialized to an ISO 8601 string
    timestamp: datetime

    def find_data(self, name: str) -> RecordData | None:
        return next((x for x in self.data if x.metric_name == name), None)


# todo: usually I use pydantic, but here the post-init is easier to do with python's native dataclass
# i don't think mixing them is a good idea; there's no necessity for a lot of data validation anyhow,
# so maybe we can move away from pydantic entirely?
@dataclass
class TempRecord:
    """
    Record that are kept in the in-memory ExpiringDict while being completed.
    """

    metrics: list[Metric]
    data: list[RecordData] = None  # initialised in __post_init__
    timestamp: datetime = datetime.now()

    # todo create tests
    def find_data(self, name: str) -> RecordData | None:
        return next((x for x in self.data if x.metric_name == name), None)

    # todo create tests
    def find_metric(self, user_prompt: str) -> Metric | None:
        return next((x for x in self.metrics if x.user_prompt == user_prompt), None)

    def update_data(self, name: str, value: int | None):
        record_data = self.find_data(name)
        if record_data:
            record_data.value = value
        else:
            raise ValueError(f"Metric {name} not found in record data.")

    def is_complete(self) -> bool:
        return all([x.value is not None for x in self.data])

    def __post_init__(self):
        self.data = [
            RecordData(metric_name=metric.name, value=None) for metric in self.metrics
        ]
