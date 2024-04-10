import datetime

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


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
