from pydantic import BaseModel

from src.model.metric import Metric


class RecordData(BaseModel):
    metric: Metric
    value: int


class Record(BaseModel):
    user_id: int
    data: list[RecordData]
