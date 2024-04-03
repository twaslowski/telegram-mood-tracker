from unittest.mock import Mock, AsyncMock

import pytest

from src.config.auto_baseline import AutoBaselineConfig
from src.handlers.user_handlers import create_user, toggle_auto_baseline


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


@pytest.mark.asyncio
async def test_update_user(update, user_repository):
    # Given a user
    update.effective_user.id = 123
    user = await create_user(update, None)

    # When the user notifications are updated
    user.notifications = []
    user_repository.update_user(user)

    # The user has no notifications when next retrieved from the database
    assert user_repository.find_user(123).notifications == []


@pytest.mark.asyncio
@pytest.mark.skip(reason="As of now, auto-baseline is not enabled upon user creation")
async def test_update_user(update, user_repository, configuration, application):
    # Given a user
    update.effective_user.id = 456
    # When a user is created with AutoBaseline enabled
    configuration.auto_baseline = AutoBaselineConfig(enabled=True, time="00:00")
    configuration.register()
    await create_user(update, None)

    # Then the job queue should include both their notifications and their auto-baseline job
    assert len(application.application.job_queue.jobs()) == 2


@pytest.mark.asyncio
async def test_toggle_auto_baseline_happy_path(update, user_repository, application):
    # Given a user with all baselines defined
    await create_user(update, None)

    # When auto-baseline is toggled
    await toggle_auto_baseline(update, None)

    # Then the auto-baseline job should be scheduled
    assert len(application.application.job_queue.jobs()) == 2  # including configuration
