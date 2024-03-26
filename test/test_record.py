import datetime
import time
from unittest.mock import Mock, AsyncMock

import pytest
from expiringdict import ExpiringDict

import src.handlers.command_handlers as command_handlers
import src.repository.record_repository as record_repository
from src.handlers.command_handlers import init_record, button, init_user
from src.model.user import User

expiry_time = 1


@pytest.fixture
def button_update():
    # mock button update
    button_update = AsyncMock()
    button_update.effective_user.id = 1
    # mock user response to first record
    mock_bot = AsyncMock()
    button_update.effective_user.get_bot = Mock(return_value=mock_bot)
    query = AsyncMock()
    query.data = "NEUTRAL"
    query.message.text = "How do you feel right now?"
    button_update.callback_query = query
    mock_bot.send_message = AsyncMock()
    return button_update


@pytest.fixture
def update():
    update = Mock()
    update.effective_user.id = 1
    update.effective_user.get_bot().send_message = AsyncMock()
    return update


@pytest.fixture(autouse=True)
def patch_command_handler_methods():
    command_handlers.temp_records = ExpiringDict(
        max_len=100, max_age_seconds=expiry_time
    )
    command_handlers.state = ExpiringDict(max_len=100, max_age_seconds=expiry_time)
    command_handlers.handle_enum_metric = AsyncMock()
    command_handlers.handle_numeric_metric = AsyncMock()
    command_handlers.handle_no_known_state = AsyncMock()


@pytest.fixture
def user() -> User:
    return User(user_id=1, metrics=test_metrics, notifications=[])


@pytest.fixture(autouse=True)
def patch_repository_methods(mocker, user):
    mocker.patch("src.repository.user_repository.find_user", return_value=user)


@pytest.mark.asyncio
async def test_init_and_expire_record(update, button_update):
    """
    Create a record and let it expire.
    """
    # create record
    await init_user(update, None)
    init_record(1)
    assert command_handlers.temp_records.get(1) is not None
    # let expiry time elapse
    time.sleep(expiry_time + 1)
    # after being emptied, the dict contains an empty list, as opposed to being empty entirely
    assert command_handlers.temp_records.get(1) is None

    # when user attempts to record, they receive an error message
    await command_handlers.button(button_update, None)
    command_handlers.handle_no_known_state.called_count = 1


@pytest.mark.asyncio
async def test_record_registration(button_update, update):
    """
    Tests the state transition from recording Metric A to Metric B.
    Does not cover the state transition from Metric N to Finished.
    """
    # when user calls /record
    await command_handlers.main_handler(update, None)

    # bot responds with first metric user prompt
    # omit this in further tests
    assert update.effective_user.get_bot().send_message.call_count == 1
    assert command_handlers.handle_enum_metric.call_count == 1

    # when user response is received
    await button(button_update, None)

    # first metric is set in the temporary record
    # omit this in further tests
    assert command_handlers.temp_records.get(1)["record"]["mood"] == "NEUTRAL"
    assert command_handlers.temp_records.get(1)["record"]["energy"] is None


@pytest.mark.asyncio
async def test_finish_record_creation(update, button_update, mocker, user):
    """
    Tests state transition from recording Metric N to Finished.
    """
    # given only one metric is defined
    mocker.patch("src.repository.user_repository.find_user", return_value=user)
    user.metrics = [test_metrics[0]]

    # when user calls /record
    await command_handlers.main_handler(update, None)

    # when user response is received
    await button(button_update, None)

    # then record creation is complete
    # verify that the temporary record has been cleaned
    assert command_handlers.temp_records.get(1) is None

    # verify record was created
    user_records = record_repository.find_records_for_user(1)
    assert len(user_records) == 1
    assert user_records[0]["record"]["mood"] == "NEUTRAL"
    assert type(user_records[0]["timestamp"]) == datetime.datetime


@pytest.mark.asyncio
async def test_double_answer_works_as_intended(update, button_update):
    """
    Verify that a user answer the same question works as intended (i.e. the previous record is overwritten).
    Extends `test_record_registration`
    :return:
    """
    # when user calls /record
    await command_handlers.main_handler(update, None)

    # when user responds with metric
    await button(button_update, None)

    # given user answers the same question again
    query = AsyncMock()
    query.data = "MODERATELY_ELEVATED"
    query.message.text = "How do you feel right now?"
    button_update.callback_query = query

    # when user responds with the same metric again
    await button(button_update, None)

    # then the record is updated
    assert (
        command_handlers.temp_records.get(1)["record"]["mood"] == "MODERATELY_ELEVATED"
    )
    assert command_handlers.temp_records.get(1)["record"]["energy"] is None


@pytest.mark.asyncio
async def test_record_with_offset(update):
    # when user calls /record
    await command_handlers.main_handler(update, None)

    # when the user offsets the record by 1 day
    offset_context = Mock()
    offset_context.args = [1]
    await command_handlers.offset_handler(update, offset_context)

    # then the temp record's timestamp should be offset by 1 day
    assert (
        datetime.datetime.fromisoformat(
            command_handlers.temp_records.get(1)["timestamp"]
        ).day
        == datetime.datetime.now().day - 1
    )


test_metrics = [
    {
        "name": "mood",
        "prompt": "How do you feel right now?",
        "type": "enum",
        "values": {
            "SEVERELY_ELEVATED": 3,
            "MODERATELY_ELEVATED": 2,
            "MILDLY_ELEVATED": -1,
            "NEUTRAL": 0,
            "MILDLY_DEPRESSED": -1,
            "MODERATELY_DEPRESSED": -2,
            "SEVERELY_DEPRESSED": -3,
        },
    },
    {
        "name": "energy",
        "type": "numeric",
        "prompt": "How much energy do you have right now?",
        "range": (1, 11),
    },
]
