import os
from unittest.mock import Mock, AsyncMock

import mongomock
import pytest
from kink import di

from src.app import MoodTrackerApplication
from src.config.auto_baseline import AutoBaselineConfig
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
    application = MoodTrackerApplication(os.getenv("TELEGRAM_TOKEN"))
    di[MoodTrackerApplication] = application
    return application


@pytest.fixture(autouse=True)
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update
