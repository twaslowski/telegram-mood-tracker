import datetime
from unittest.mock import Mock, AsyncMock

import pytest

from src.handlers.user_handlers import create_user


@pytest.mark.asyncio
async def test_auto_baseline_happy_path_if_no_other_records_exist(
    update, notifier, repositories
):
    record_repository = repositories.record_repository
    # Given a user
    user = await create_user(update, None)
    context = Mock()
    context.bot.send_message = AsyncMock()

    # When auto-baseline is called
    await notifier.auto_baseline(context, user)

    # Then a record is created
    record = record_repository.get_latest_record_for_user(user.user_id)
    assert record is not None

    # And the record holds the user's baseline values
    assert record.data["mood"] == user.get_metric_by_name("mood").baseline
    assert record.data["sleep"] == user.get_metric_by_name("sleep").baseline


@pytest.mark.asyncio
async def test_auto_baseline_happy_path_if_record_exists_from_yesterday(
    update, notifier, repositories
):
    record_repository = repositories.record_repository
    # Given a user
    user = await create_user(update, None)
    context = Mock()
    context.bot.send_message = AsyncMock()

    # And a record from yesterday
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    record_repository.create_record(user.user_id, {}, yesterday.isoformat())

    # When auto-baseline is called
    await notifier.auto_baseline(context, user)

    # Then a record is created
    assert len(records := record_repository.find_records_for_user(user.user_id)) == 2
    assert records[0].timestamp.date().day == yesterday.day
    assert records[1].timestamp.date().day == datetime.datetime.now().date().day


@pytest.mark.asyncio
async def test_auto_baseline_wont_create_record_if_record_already_exists_for_the_day(
    update, notifier, repositories
):
    record_repository = repositories.record_repository
    # Given a user
    user = await create_user(update, None)
    context = Mock()
    context.bot.send_message = AsyncMock()

    # And a record for today
    record_repository.create_record(
        user.user_id, {}, datetime.datetime.now().isoformat()
    )

    # exactly one record exists
    assert len(record_repository.find_records_for_user(user.user_id)) == 1

    # When auto-baseline is called
    await notifier.auto_baseline(context, user)

    # Then no new record is created
    assert len(record_repository.find_records_for_user(user.user_id)) == 1
