from pydantic import BaseModel


class RecordData(BaseModel):
    metric_name: str
    value: int


class Record(BaseModel):
    user_id: int
    data: list[RecordData]
