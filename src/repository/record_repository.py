import logging
from abc import ABC
import datetime
from abc import abstractmethod

from pyautowire import Injectable
from src.model.record import Record


class RecordRepository(Injectable, ABC):
    @staticmethod
    def parse_record(result: dict) -> Record:
        return Record(**result)

    @staticmethod
    def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
        timestamp = datetime.datetime.fromisoformat(timestamp)
        return timestamp - datetime.timedelta(days=offset)

    @abstractmethod
    def get_latest_record_for_user(self, user_id: int) -> Record | None:
        pass

    @abstractmethod
    def create_record(self, user_id: int, record_data: dict, timestamp: str):
        pass

    @abstractmethod
    def find_records_for_user(self, user_id: int) -> list[Record]:
        pass

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
