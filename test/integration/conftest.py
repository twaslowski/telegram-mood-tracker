import os
from unittest.mock import Mock, AsyncMock

import boto3
import mongomock
import pytest
from botocore.stub import Stubber
from kink import di

from src.app import MoodTrackerApplication
from src.config.auto_baseline import AutoBaselineConfig
from src.config.config import ConfigurationProvider
from src.notifier import Notifier
from src.repository.dynamodb.dynamodb_user_repository import DynamoDBUserRepository
from src.repository.mongodb.user_repository import MongoDBUserRepository
from src.repository.record_repository import RecordRepository
from src.service.user_service import UserService

"""
Pytest Fixture setup.
Creates fixtures and registers Injectables for tests.
The name is required by pytest convention.
"""


@pytest.fixture(autouse=True)
def mock_client():
    return mongomock.MongoClient()


@pytest.fixture(autouse=True)
def dynamodb():
    dynamodb = boto3.resource("dynamodb")
    stubber = Stubber(dynamodb.meta.client)
    # add responses here
    stubber.add_response("describe_table", {})

    stubber.activate()
    return dynamodb


@pytest.fixture(autouse=True)
def dynamodb_user_repository(dynamodb):
    dynamodb_user_repository = DynamoDBUserRepository(dynamodb)
    return dynamodb_user_repository.register(alias="user_repository")


@pytest.fixture(autouse=True)
def mongodb_user_repository(mock_client):
    user_repository = MongoDBUserRepository(mock_client)
    # user_repository.register(alias="user_repository")
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
def auto_baseline_config():
    return AutoBaselineConfig(
        **{
            "enabled": True,
            "time": "12:00",
        }
    )


@pytest.fixture(autouse=True)
def application():
    # initializes application, registers notifier implicitly
    # real token only needed for notification tests, as of now
    application = MoodTrackerApplication(os.getenv("TELEGRAM_TOKEN", "some-token"))
    di[MoodTrackerApplication] = application
    return application


@pytest.fixture(autouse=True)
def user_service():
    user_service = UserService()
    user_service.register()


@pytest.fixture(autouse=True)
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update


@pytest.fixture(autouse=True)
def notifier():
    # registered via the application init; this is simply convenience for tests
    return di[Notifier.get_fully_qualified_name()]
