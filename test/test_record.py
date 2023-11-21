import logging
import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

from expiringdict import ExpiringDict

import src.handlers.command_handlers as command_handlers
import src.persistence as persistence
from src.handlers.command_handlers import init_record
from src.handlers.command_handlers import init_user


class TestRecord(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        update = Mock()
        update.effective_user.id = 1
        command_handlers.temp_records = ExpiringDict(max_len=100, max_age_seconds=5)
        command_handlers.user_record_registration_state = ExpiringDict(max_len=100, max_age_seconds=5)
        await init_user(update, None)

    async def asyncTearDown(self) -> None:
        persistence.user.delete_many({})

    def test_init_and_invalidate_record(self):
        # create record
        init_record(1)
        self.assertIsNotNone(command_handlers.temp_records.get(1))
        self.assertEqual(command_handlers.user_record_registration_state.get(1),
                         persistence.user.find_one({'user_id': 1})['metrics'])
        # let expiry time elapse
        time.sleep(6)
        # after being emptied, the dict contains an empty list, as opposed to being empty entirely
        self.assertIsNone(command_handlers.temp_records.get(1))
        self.assertIsNone(command_handlers.user_record_registration_state.get(1))
