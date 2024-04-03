import os

import mongomock
import pytest
from kink import di

from src.app import MoodTrackerApplication
from src.config.config import ConfigurationProvider
from src.repository.record_repository import RecordRepository
from src.repository.user_repository import UserRepository


@pytest.fixture(autouse=True)
def mock_client():
    return mongomock.MongoClient()


@pytest.fixture(autouse=True)
def user_repository(mock_client):
    user_repository = UserRepository(mock_client)
    user_repository.register()
    return user_repository


@pytest.fixture(autouse=True)
def record_repository(mock_client):
    record_repository = RecordRepository(mock_client)
    record_repository.register()
    return record_repository


@pytest.fixture(autouse=True)
def configuration():
    configuration = ConfigurationProvider(
        "test/resources/config.test.yaml"
    ).get_configuration()
    configuration.register()
    return configuration


@pytest.fixture(autouse=True)
def application():
    # initializes application, registers notifier implicitly
    application = MoodTrackerApplication(os.getenv("TELEGRAM_TOKEN"))
    di[MoodTrackerApplication] = application
    return application
