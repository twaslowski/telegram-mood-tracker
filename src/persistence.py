from pymongo import MongoClient
from src.data.record import MoodRecord


class MoodRecordDB:
    def __init__(self, db_url: str, db_name: str):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]

    def save_record(self, record: MoodRecord):
        self.db.records.insert_one(record.__dict__)

    def get_records(self):
        return [MoodRecord(**record) for record in self.db.records.find()]
