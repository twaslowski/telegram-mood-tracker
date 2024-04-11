import datetime

import boto3
from boto3.dynamodb.conditions import Key

from src.model.record import Record
from src.repository.record_repository import RecordRepository


class DynamoDBRecordRepository(RecordRepository):
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


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
