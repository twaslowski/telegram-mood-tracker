import datetime
import logging

import boto3
from boto3.dynamodb.conditions import Key

from pyautowire import Injectable
from src.model.record import Record, DatabaseRecord


class DynamoDBRecordRepository(Injectable):
    def __init__(self, dynamodb: boto3.resource):
        self.table = dynamodb.Table("record")
        self.table.load()

    def get_latest_record_for_user(self, user_id: int) -> Record | None:
        result = self.table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=1,
        )
        if result.get("Items"):
            return self.parse_record(result["Items"][0])

    @staticmethod
    def parse_record(result: dict) -> Record:
        result = DatabaseRecord(**result)
        # transform the record data to a list of RecordData objects
        return result.to_record()

    def create_record(self, user_id: int, record_data: dict, timestamp: str):
        self.table.put_item(
            Item={"user_id": user_id, "record": record_data, "timestamp": timestamp}
        )

    def find_records_for_user(self, user_id: int) -> list[Record]:
        return [
            self.parse_record(r)
            for r in list(
                self.table.query(KeyConditionExpression=Key("user_id").eq(user_id))[
                    "Items"
                ]
            )
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


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
