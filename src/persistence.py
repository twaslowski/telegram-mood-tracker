import pymongo

mongo_url = "mongodb://localhost:27017/"
mongo_client = pymongo.MongoClient(mongo_url)
records_db = mongo_client["records"]
records = records_db["records"]


def init() -> None:
    records.create_collection("records")


def save_record(record: dict) -> None:
    records.insert_one(record)


def list_records() -> list:
    return list(records.find({}))


def get_latest_record() -> dict:
    return records.find_one({}, sort=[("timestamp", pymongo.DESCENDING)])


def update_latest_record(record: dict) -> None:
    latest = get_latest_record()
    latest.update(record)
    records.replace_one({"_id": latest["_id"]}, latest)


def delete_all() -> None:
    records.delete_many({})
