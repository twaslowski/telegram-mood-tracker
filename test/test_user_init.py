from unittest.async_case import IsolatedAsyncioTestCase

from telegram.ext import ApplicationBuilder
from unittest.mock import Mock, AsyncMock

import src.persistence as persistence
from src.app import init_reminders
from src.handlers.command_handlers import init_user


class TestUser(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        update = Mock()
        update.effective_user.id = 1
        update.effective_user.get_bot().send_message = AsyncMock()
        await init_user(update, None)

    async def asyncTearDown(self) -> None:
        persistence.user.delete_many({})

    async def test_registration(self):
        user = persistence.user.find_one({"user_id": 1})
        self.assertIsNotNone(user)
        self.assertIsNotNone(user['metrics'])
        self.assertEqual(len(user['metrics']), 8)
        self.assertIsNotNone(user['notifications'])

    async def test_no_double_registration(self):
        update = Mock()
        update.effective_user.id = 1
        await init_user(update, None)
        users = persistence.user.find({"user_id": 1})
        self.assertEqual(len(list(users)), 1)

    async def test_notifications(self):
        # create additional user
        update = Mock()
        update.effective_user.id = 2
        update.effective_user.get_bot().send_message = AsyncMock()
        await init_user(update, None)

        # init app with notification settings
        app = ApplicationBuilder().token('some-token').build()
        init_reminders(app)
        self.assertEqual(len(app.job_queue.jobs()), 4)
