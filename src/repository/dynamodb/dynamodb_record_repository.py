import datetime
import logging

import boto3
from boto3.dynamodb.conditions import Key

from src.model.record import Record
from src.repository.record_repository import RecordRepository


class DynamoDBRecordRepository(RecordRepository):
    def __init__(self, dynamodb: boto3.resource):
        self.table = dynamodb.Table("record")
        self.table.load()
        logging.info("DynamoDBRecordRepository initialized.")

    def get_latest_record_for_user(self, user_id: int) -> Record | None:
        result = self.get_latest_records_for_user(user_id, 1)
        if result:
            return result[0]

    def get_latest_records_for_user(
        self, user_id: int, limit: int
    ) -> list[Record] | None:
        logging.info(f"Retrieving {limit} latest records for user {user_id}")
        result = self.table.query(
            KeyConditionExpression=Key("user_id").eq(user_id),
            ScanIndexForward=False,
            Limit=limit,
        )
        if result.get("Items"):
            return [self.parse_record(record) for record in result["Items"]]
        return []

    def create_record(self, user_id: int, record_data: dict, timestamp: str):
        self.table.put_item(
            Item={"user_id": user_id, "data": record_data, "timestamp": timestamp}
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

    def save_record(self, record: Record):
        self.table.put_item(Item=record.serialize())

    def find_records_for_time_range(
        self, user_id: int, beginning: datetime.datetime, end: datetime.datetime
    ) -> list[Record]:
        return [
            self.parse_record(r)
            for r in self.table.scan(
                FilterExpression=Key("user_id").eq(user_id)
                & Key("timestamp").between(beginning.isoformat(), end.isoformat())
            )["Items"]
        ]


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
