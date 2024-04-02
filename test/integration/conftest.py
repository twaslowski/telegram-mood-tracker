from unittest.mock import patch

import mongomock
import pymongo
import pytest
from kink import di

from src.app import MoodTrackerApplication
from src.config import ConfigurationProvider
from src.repository import record_repository
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
def patch_records_collection():
    with patch.object(
            record_repository, "records", new=mongomock.MongoClient().db.collection
    ):
        yield


@pytest.fixture(autouse=True)
def configuration():
    ConfigurationProvider("test/resources/config.test.yaml").get_configuration().register()


@pytest.fixture(autouse=True)
def application():
    # initializes application, registers notifier implicitly
    application = MoodTrackerApplication("some-token")
    di[MoodTrackerApplication] = application
    return application

