from unittest.mock import Mock, AsyncMock

import pytest
from telegram.ext import ApplicationBuilder

import src.repository.user_repository as user_repository
from src.app import init_reminders
from src.handlers.command_handlers import init_user


@pytest.fixture
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update


def test_querying_nonexistent_user_returns_none():
    assert user_repository.find_user(1) is None


@pytest.mark.asyncio
async def test_registration(update):
    # user does not exist
    assert user_repository.find_user(1) is None

    # create user
    await init_user(update, None)

    # now it exists
    assert user_repository.find_user(1) is not None
    assert user_repository.find_user(1).metrics is not None
    assert user_repository.find_user(1).notifications is not None

    # introductory text has been sent
    assert update.effective_user.get_bot().send_message.called


@pytest.mark.asyncio
async def test_no_double_registration(update):
    # user does not exist
    assert user_repository.find_user(1) is None

    # user is created
    await init_user(update, None)
    assert update.effective_user.get_bot().send_message.call_count == 1

    # user creation is not repeated
    await init_user(update, None)
    assert update.effective_user.get_bot().send_message.call_count == 1


@pytest.mark.asyncio
async def test_notifications(update):
    # create additional user
    await init_user(update, None)

    # init app with notification settings
    app = ApplicationBuilder().token("some-token").build()
    init_reminders(app)
    assert len(app.job_queue.jobs()) == 1
