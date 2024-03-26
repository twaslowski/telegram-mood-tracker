import datetime

from pydantic import BaseModel


class RecordData(BaseModel):
    # chosen like this for backward compatibility
    metric_name: str
    value: int


class Record(BaseModel):
    user_id: int
    # this name is very unintuitive, as it overloads the meaning of the word "record"
    # it is chosen like this for backward compatibility,
    # but it should be migrated to something like 'data' or 'record_data' in the future
    record: list[RecordData]
    # gets serialized to an ISO 8601 string
    timestamp: datetime.datetime
