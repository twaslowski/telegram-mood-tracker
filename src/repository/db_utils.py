"""
Mechanisms for manually interacting with the database for diagnostics work etc.
"""
import logging
import os

from src.config.config import ConfigurationProvider
from src.repository.initialize import initialize_database
from src.repository.record_repository import RecordRepository
from src.repository.user_repository import UserRepository


def init() -> (UserRepository, RecordRepository):
    configuration = ConfigurationProvider().get_configuration().register()
    return initialize_database(configuration)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    user_id = int(os.getenv("USER_ID"))
    user_repository, record_repository = init()
    for record in record_repository.get_latest_records_for_user(user_id, 2):
        print(record)
