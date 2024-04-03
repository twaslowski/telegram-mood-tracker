from unittest.mock import Mock, AsyncMock

import pytest

from src.app import MoodTrackerApplication
from kink import di

from src.config import ConfigurationProvider
from src.handlers.user_handlers import create_user
from src.notifier import Notifier


@pytest.fixture
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update


def test_querying_nonexistent_user_returns_none(user_repository):
    assert user_repository.find_user(1) is None


@pytest.mark.asyncio
async def test_registration(update, user_repository):
    # user does not exist
    assert user_repository.find_user(1) is None

    # create user
    await create_user(update, None)

    # now it exists
    assert user_repository.find_user(1) is not None
    assert user_repository.find_user(1).metrics is not None
    assert user_repository.find_user(1).notifications is not None

    # introductory text has been sent
    assert update.effective_user.get_bot().send_message.called


@pytest.mark.asyncio
async def test_notifications(update, application):
    await create_user(update, None)

    assert len(application.application.job_queue.jobs()) == 1
