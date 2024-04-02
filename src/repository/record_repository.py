import datetime

import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient

from src.autowiring.injectable import Injectable
from src.model.record import Record, RecordData, DatabaseRecord


class RecordRepository(Injectable):
    def __init__(self, mongo_client: MongoClient):
        mood_tracker = mongo_client["mood_tracker"]
        self.records = mood_tracker["records"]

    def get_latest_record_for_user(self, user_id: int) -> Record | None:
        result = self.records.find_one(
            {"user_id": user_id}, sort=[("timestamp", pymongo.DESCENDING)]
        )
        if result:
            return self.parse_record(dict(result))

    @staticmethod
    def parse_record(result: dict) -> Record:
        result = DatabaseRecord(**result)
        # transform the record data to a list of RecordData objects
        return result.to_record()

    def create_record(self, user_id: int, record_data: dict, timestamp: str):
        self.records.insert_one(
            {"user_id": user_id, "record": record_data, "timestamp": timestamp}
        )

    def find_records_for_user(self, user_id: int) -> list[Record]:
        return [
            self.parse_record(r) for r in list(self.records.find({"user_id": user_id}))
        ]

    def zeroes(self, days: int):
        """
        Inserts records with default values for missed days within a date range.
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.
        """

        user_id = 1965256751
        default_record = {"sleep": "8", "mood": "0"}
        start = datetime.datetime.now().isoformat()
        date_range = [modify_timestamp(start, n).isoformat() for n in range(days)]

        for date in date_range:
            print(f"Inserting neutral record for timestamp {date}")
            self.create_record(user_id, default_record, date)


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
