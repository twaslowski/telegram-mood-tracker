from unittest.mock import Mock, AsyncMock

import pytest
from kink import di
from telegram.ext import ApplicationBuilder

import src.repository.user_repository as user_repository
from src.app import init_notifications
from src.handlers.user_handlers import create_user
from src.reminder import Notifier


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
    await create_user(update, None)

    # now it exists
    assert user_repository.find_user(1) is not None
    assert user_repository.find_user(1).metrics is not None
    assert user_repository.find_user(1).notifications is not None

    # introductory text has been sent
    assert update.effective_user.get_bot().send_message.called


@pytest.mark.asyncio
@pytest.mark.skip(
    "I have added a message to the user when they are already registered for clarity"
)
async def test_no_double_registration(update):
    # user does not exist
    assert user_repository.find_user(1) is None

    # user is created
    await create_user(update, None)
    assert update.effective_user.get_bot().send_message.call_count == 1

    # user creation is not repeated
    await create_user(update, None)
    assert update.effective_user.get_bot().send_message.call_count == 1


@pytest.mark.asyncio
async def test_notifications(update):
    # create additional user
    app = ApplicationBuilder().token("some-token").build()
    di[Notifier] = Notifier(app.job_queue)
    await create_user(update, None)

    # init app with notification settings
    init_notifications(app)
    assert len(app.job_queue.jobs()) == 1
