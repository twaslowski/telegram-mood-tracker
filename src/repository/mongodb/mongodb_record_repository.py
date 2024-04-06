import datetime
import logging

import pymongo
from pymongo import MongoClient

from src.model.record import Record
from src.repository.record_repository import RecordRepository


class MongoDBRecordRepository(RecordRepository):
    def __init__(self, mongo_client: MongoClient):
        super().__init__()
        mood_tracker = mongo_client["mood_tracker"]
        self.records = mood_tracker["records"]

    def get_latest_record_for_user(self, user_id: int) -> Record | None:
        result = self.records.find_one(
            {"user_id": user_id}, sort=[("timestamp", pymongo.DESCENDING)]
        )
        if result:
            return self.parse_record(dict(result))

    def create_record(self, user_id: int, record_data: dict, timestamp: str):
        self.records.insert_one(
            {"user_id": user_id, "data": record_data, "timestamp": timestamp}
        )

    def find_records_for_user(self, user_id: int) -> list[Record]:
        return [
            self.parse_record(r) for r in list(self.records.find({"user_id": user_id}))
        ]

    def zeroes(self, from_date: datetime.date, to_date: datetime.date):
        """
        Inserts records with default values for missed days within a date range.
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.
        """

        user_id = 1965256751
        default_record = {"sleep": "8", "mood": "0"}
        date_range = [
            from_date + datetime.timedelta(days=i)
            for i in range((to_date - from_date).days + 1)
        ]

        for date in date_range:
            logging.info(f"Inserting neutral record for timestamp {date}")
            self.create_record(user_id, default_record, f"{date}T12:00:00.000000")

    def find_records_for_time_range(
            self, user_id: int, beginning: datetime.datetime, end: datetime.datetime
    ) -> list[Record]:
        logging.info(
            f"Retrieving data for between {beginning} and {end} for user {user_id}"
        )
        return [
            self.parse_record(r)
            for r in list(
                self.records.find(
                    {
                        "user_id": user_id,
                        "timestamp": {
                            "$gte": beginning.isoformat(),
                            "$lte": end.isoformat(),
                        },
                    }
                )
            )
        ]
