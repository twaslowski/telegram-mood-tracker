from unittest.mock import Mock, AsyncMock

import pytest
from tenacity import RetryError

from src.handlers.util import send


@pytest.fixture
def context():
    context = Mock()
    context.bot.send_message = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_message_gets_retried(update):
    # Given that when send_message() is called for the first time, it raises a TimeoutError
    update.effective_user.get_bot().send_message.side_effect = [TimeoutError(), None]

    # Exception does not have to be caught because of the retry decorator
    await send(update, "Hello")

    # Then a message should be sent again
    assert update.effective_user.get_bot().send_message.call_count == 2


@pytest.mark.asyncio
async def test_message_gets_retried_three_times(update):
    # Given that when send_message() is called, it raises a TimeoutError
    update.effective_user.get_bot().send_message.side_effect = TimeoutError()

    # Exception does not have to be caught because of the retry decorator
    with pytest.raises(RetryError):
        await send(update, "Hello")

    # Then a message should be sent again
    assert update.effective_user.get_bot().send_message.call_count == 3


@pytest.mark.asyncio
async def test_reminder_gets_retried(context, notifier):
    # Given that when send_from_context() is called for the first time, it raises a TimeoutError
    context.bot.send_message.side_effect = [TimeoutError(), None]

    # Exception does not have to be caught because of the retry decorator
    await notifier.reminder(context, 1, "Hello!")

    # Then a message should be sent again
    assert context.bot.send_message.call_count == 2


@pytest.mark.asyncio
async def test_reminder_gets_retried(context, notifier):
    # Given that when send_from_context() is called for the first time, it raises a TimeoutError
    context.bot.send_message.side_effect = TimeoutError()

    # Exception does not have to be caught because of the retry decorator
    with pytest.raises(RetryError):
        await notifier.reminder(context, 1, "Hello!")

    # Then a message should be sent again
    assert context.bot.send_message.call_count == 3
