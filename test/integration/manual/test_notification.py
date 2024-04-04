import asyncio
import logging
import unittest.mock
from datetime import datetime, timedelta

import pytest
import telegram.error
from kink import di
from nest_asyncio import apply
from telegram.ext import ContextTypes, Application

from src.config.auto_baseline import AutoBaselineConfig
from src.handlers.user_handlers import create_user
from src.model.notification import Notification
from src.notifier import Notifier


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="I have not found a test to make the application terminate, so this runs indefinitely."
)
async def test_notification(application, configuration):
    # Given a notification with a fixed time
    notification = Notification(time=generate_time(), text="Test notification.")
    notifier = get_notifier()
    notifier.create_notification(123456, notification)

    # Utility: Add an error handler to the application
    add_error_handler(application.application)

    with unittest.mock.patch("src.notifier.Notifier.reminder"):
        # When the application runs
        loop = asyncio.get_event_loop()
        apply()
        loop.create_task(application.run())


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="I have not found a test to make the application terminate, so this runs indefinitely."
)
async def test_auto_baseline(update, application, configuration, user_repository):
    now = generate_time()

    # Given an existing user with auto-baseline enabled
    await create_user(update, None)
    user = user_repository.find_user(1)
    user.auto_baseline_config = AutoBaselineConfig(enabled=True, time=now)
    user_repository.update_user(user)

    # Given a notification with a fixed time
    notifier = get_notifier()
    notifier.create_auto_baseline(user)

    # Utility: Add an error handler to the application
    add_error_handler(application.application)

    with unittest.mock.patch("src.notifier.Notifier.auto_baseline"):
        # When the application runs
        loop = asyncio.get_event_loop()
        apply()
        loop.create_task(application.run())


def generate_time():
    return (datetime.now().utcnow() + timedelta(seconds=2)).time()


def get_notifier():
    return di[Notifier.get_fully_qualified_name()]


def add_error_handler(application: Application):
    logging.info("Adding error handler")

    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("Encountered expected error.")

    application.add_error_handler(error_handler)
