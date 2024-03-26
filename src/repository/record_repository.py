import datetime
import os

import pymongo
from dotenv import load_dotenv

from src.model.record import Record

# use bracket notation over .get() to fail explicitly if environment variable is not supplied
mongo_url = os.getenv("MONGODB_HOST", "localhost:27017")
mongo_client = pymongo.MongoClient(f"mongodb://{mongo_url}/")
mood_tracker = mongo_client["mood_tracker"]
records = mood_tracker["records"]


def get_latest_record() -> Record:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])
    # if result:
    #     return parse_record(dict(result))


def parse_record(result: dict):
    result = dict(result)
    assert result["timestamp"]
    result["timestamp"] = datetime.datetime.fromisoformat(result["timestamp"])
    return Record(**result)


def create_record(user_id: int, record_data: dict, timestamp: str):
    records.insert_one(
        {"user_id": user_id, "record": record_data, "timestamp": timestamp}
    )


def find_records_for_user(user_id: int) -> list[Record]:
    return [parse_record(r) for r in list(records.find({"user_id": user_id}))]


def zeroes(days: int):
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
        create_record(user_id, default_record, date)


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
