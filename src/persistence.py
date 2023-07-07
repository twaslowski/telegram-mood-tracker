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


def delete_all() -> None:
    records.delete_many({})
