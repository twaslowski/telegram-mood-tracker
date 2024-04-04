import asyncio

import pytest
from nest_asyncio import apply
from telegram.ext import CommandHandler


@pytest.mark.asyncio
async def test_error_handler_message_contains_exception_text(application):
    async def exception_throwing_handler(update, context):
        raise Exception("This is a test exception")

    # manually throw exception on staging environment
    application.application.add_handler(
        CommandHandler("exception", exception_throwing_handler)
    )
    apply()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.run())
