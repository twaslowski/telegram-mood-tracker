import datetime


from pyautowire import Injectable
from src.model.record import Record, DatabaseRecord


class RecordRepository(Injectable):
    @staticmethod
    def parse_record(result: dict) -> Record:
        result = DatabaseRecord(**result)
        # transform the record data to a list of RecordData objects
        return result.to_record()


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
