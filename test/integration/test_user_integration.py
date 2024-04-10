from collections import OrderedDict
from unittest.mock import Mock, AsyncMock

import pytest

from src.config.auto_baseline import AutoBaselineConfig
from src.exception.auto_baseline_exception import MetricBaselinesNotDefinedException
from src.handlers.user_handlers import create_user, toggle_auto_baseline
from src.service.user_service import AutoBaselineTimeNotDefinedException


@pytest.fixture
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update


def test_querying_nonexistent_user_returns_none(repositories):
    user_repository = repositories.user_repository
    assert user_repository.find_user(1) is None


@pytest.mark.asyncio
async def test_return_value_of_user_creation(update, repositories):
    user_repository = repositories.user_repository
    user = await create_user(update, None)
    assert user.user_id == 1
    assert user.metrics is not None
    assert user.notifications is not None

    assert user == user_repository.find_user(1)


@pytest.mark.asyncio
async def test_registration(update, repositories):
    user_repository = repositories.user_repository
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
async def test_update_user(update, configuration, application):
    # Given a user
    update.effective_user.id = 456
    # When a user is created with AutoBaseline enabled
    configuration.auto_baseline = AutoBaselineConfig(enabled=True, time="00:00")
    configuration.register()
    await create_user(update, None)

    # Then the job queue should include both their notifications and their auto-baseline job
    assert len(application.application.job_queue.jobs()) == 2


@pytest.mark.asyncio
async def test_toggle_auto_baseline_happy_path(update, repositories, application):
    user_repository = repositories.user_repository
    # Given a user with all baselines defined and auto-baseline disabled (and time configured)
    await create_user(update, None)
    assert user_repository.find_user(1).has_auto_baseline_enabled() is False

    # When auto-baseline is toggled
    await toggle_auto_baseline(update, None)

    # Then the auto-baseline job should be scheduled
    assert len(application.application.job_queue.jobs()) == 2  # including configuration
    assert user_repository.find_user(1).has_auto_baseline_enabled() is True

    # When auto-baseline is toggled again
    await toggle_auto_baseline(update, None)

    # Then the auto-baseline job should be removed
    assert len(application.application.job_queue.jobs()) == 1
    assert user_repository.find_user(1).has_auto_baseline_enabled() is False


@pytest.mark.asyncio
async def test_toggle_auto_baseline_without_auto_baseline_time_configured(
    update, repositories, notifier
):
    user_repository = repositories.user_repository
    # Given a user with all baselines defined but no auto-baseline time configured
    user = await create_user(update, None)
    user.auto_baseline_config.time = None
    user_repository.update_user(user)

    # When auto-baseline is toggled
    with pytest.raises(AutoBaselineTimeNotDefinedException):
        await toggle_auto_baseline(update, None)

    # the user config should remain the same and no jobs have been added to the queue
    assert user_repository.find_user(1).has_auto_baseline_enabled() is False
    assert len(notifier.job_queue.jobs()) == 1


@pytest.mark.asyncio
async def test_toggle_auto_baseline_without_all_baselines_defined(
    update, repositories, notifier
):
    user_repository = repositories.user_repository
    # Given a user with not all baselines defined
    user = await create_user(update, None)
    user.metrics = []
    user_repository.update_user(user)

    # When auto-baseline is toggled
    with pytest.raises(MetricBaselinesNotDefinedException):
        await toggle_auto_baseline(update, None)

    # the user config should remain the same and no jobs have been added to the queue
    assert user_repository.find_user(1).has_auto_baseline_enabled() is False
    assert len(notifier.job_queue.jobs()) == 1


@pytest.mark.asyncio
async def test_toggle_auto_baseline_on_user_creation_if_enabled(
    update, configuration, notifier
):
    # Given a configuration with auto-baseline enabled
    configuration.auto_baseline.enabled = True
    configuration.register()

    # When a user is created
    user = await create_user(update, None)
    assert user.has_auto_baseline_enabled() is True

    # Then the auto-baseline job should be scheduled
    assert len(notifier.job_queue.jobs()) == 2  # including notifications


@pytest.mark.asyncio
async def test_should_not_create_auto_baseline_on_user_creation_if_enabled_without_time(
    update, configuration, notifier
):
    # Given a configuration with auto-baseline enabled but no time configured
    configuration.auto_baseline.enabled = True
    configuration.auto_baseline.time = None
    configuration.register()

    # When a user is created
    with pytest.raises(ValueError):
        await create_user(update, None)


@pytest.mark.asyncio
async def test_metric_order_is_retained(update, repositories):
    # This is a regression test for the DynamoDB migration.
    # Given a user with a set of ordered metrics
    user = await create_user(update, None)
    metrics = user.metrics

    # When the user is retrieved from the database
    db_user = repositories.user_repository.find_user(1)
    db_metrics = db_user.metrics

    # Then the order of the metrics should be retained
    for metric, db_metric in zip(metrics, db_metrics):
        assert OrderedDict(metric.values) == OrderedDict(db_metric.values)
