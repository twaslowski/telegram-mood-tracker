from pydantic import BaseModel

from src.model.metric import Metric


class RecordData(BaseModel):
    metric: Metric
    value: str  # todo this can be done better


class Record(BaseModel):
    user_id: int
    data: list[RecordData]
