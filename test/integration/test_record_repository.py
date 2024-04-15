import pytest

from src.handlers.user_handlers import create_user


@pytest.mark.asyncio
async def test_should_retrieve_one_record_for_current_month(update):
    # Given a user
    user = await create_user(update, None)
    ...
