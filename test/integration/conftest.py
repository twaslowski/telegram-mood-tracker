import os
from unittest.mock import Mock, AsyncMock

import boto3
import mongomock
import pytest
from kink import di

from src.app import MoodTrackerApplication
from src.config.auto_baseline import AutoBaselineConfig
from src.config.config import ConfigurationProvider
from src.notifier import Notifier
from src.repository.dynamodb.dynamodb_record_repository import DynamoDBRecordRepository
from src.repository.dynamodb.dynamodb_user_repository import DynamoDBUserRepository
from src.repository.mongodb.record_repository import MongoDBRecordRepository
from src.repository.mongodb.user_repository import MongoDBUserRepository
from src.service.user_service import UserService

"""
Pytest Fixture setup.
Creates fixtures and registers Injectables for tests.
The name is required by pytest convention.
"""


@pytest.fixture
def mongo_client():
    return mongomock.MongoClient()


@pytest.fixture
def mongodb_user_repository(mongo_client):
    mongodb_user_repository = MongoDBUserRepository(mongo_client).register(
        alias="user_repository"
    )
    return mongodb_user_repository


@pytest.fixture
def mongodb_record_repository(mongo_client):
    record_repository = MongoDBRecordRepository(mongo_client).register(
        alias="record_repository"
    )
    return record_repository


@pytest.fixture
def dynamodb():
    dynamodb = boto3.resource("dynamodb", endpoint_url="http://localhost:4566")
    return dynamodb


@pytest.fixture
def dynamodb_user_repository(dynamodb):
    dynamodb.create_table(
        TableName="user",
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "N"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb_user_repository = DynamoDBUserRepository(dynamodb).register(
        alias="user_repository"
    )
    yield dynamodb_user_repository
    dynamodb_user_repository.table.delete()


@pytest.fixture
def dynamodb_record_repository(dynamodb):
    dynamodb.create_table(
        TableName="record",
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "N"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    record_repository = DynamoDBRecordRepository(dynamodb).register(
        alias="record_repository"
    )
    yield record_repository
    record_repository.table.delete()


@pytest.fixture(params=["dynamodb_user_repository"])
def user_repository(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(params=["dynamodb_record_repository"])
def record_repository(request):
    return request.getfixturevalue(request.param)


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
def user_service(user_repository):
    user_service = UserService(user_repository=user_repository)
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
