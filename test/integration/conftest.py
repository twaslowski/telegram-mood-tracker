import os
from collections import namedtuple
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
from src.repository.mongodb.mongodb_record_repository import MongoDBRecordRepository
from src.repository.mongodb.mongodb_user_repository import MongoDBUserRepository
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
    mongodb_user_repository = MongoDBUserRepository(mongo_client)
    return mongodb_user_repository


@pytest.fixture
def mongodb_record_repository(mongo_client):
    record_repository = MongoDBRecordRepository(mongo_client)
    return record_repository


@pytest.fixture
def dynamodb():
    dynamodb = boto3.resource(
        "dynamodb", endpoint_url="http://localhost:4566", region_name="us-east-1"
    )
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
    dynamodb_user_repository = DynamoDBUserRepository(dynamodb)
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
    record_repository = DynamoDBRecordRepository(dynamodb)
    yield record_repository
    record_repository.table.delete()


# Declare Repositories named tuple for easier access in tests
Repositories = namedtuple("Repositories", ["user_repository", "record_repository"])


@pytest.fixture(params=["mongodb", "dynamodb"])
def repositories(
    request,
    mongodb_user_repository,
    mongodb_record_repository,
    dynamodb_user_repository,
    dynamodb_record_repository,
):
    persistence_backend = request.param
    if persistence_backend == "mongodb":
        user_repository = mongodb_user_repository.register(alias="user_repository")
        record_repository = mongodb_record_repository.register(
            alias="record_repository"
        )
    else:
        user_repository = dynamodb_user_repository.register(alias="user_repository")
        record_repository = dynamodb_record_repository.register(
            alias="record_repository"
        )
    return Repositories(
        user_repository=user_repository, record_repository=record_repository
    )


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
def user_service(repositories):
    user_repository = repositories.user_repository
    user_service = UserService(user_repository=user_repository)
    return user_service.register()


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
