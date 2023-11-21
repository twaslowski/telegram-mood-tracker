import logging
import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from expiringdict import ExpiringDict

import src.handlers.command_handlers as command_handlers
import src.persistence as persistence
from src.handlers.command_handlers import init_record
from src.handlers.command_handlers import init_user


class TestRecord(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        # set up update object
        self.update = Mock()
        self.update.effective_user.id = 1
        self.update.effective_user.get_bot().send_message = AsyncMock()
        command_handlers.temp_records = ExpiringDict(max_len=100, max_age_seconds=5)
        command_handlers.user_record_registration_state = ExpiringDict(max_len=100, max_age_seconds=5)

    async def asyncTearDown(self) -> None:
        persistence.user.delete_many({})

    async def test_init_and_invalidate_record(self):
        # create record
        init_user(self.update, None)
        init_record(1)
        self.assertIsNotNone(command_handlers.temp_records.get(1))
        self.assertEqual(command_handlers.user_record_registration_state.get(1),
                         persistence.user.find_one({'user_id': 1})['metrics'])
        # let expiry time elapse
        time.sleep(6)
        # after being emptied, the dict contains an empty list, as opposed to being empty entirely
        self.assertIsNone(command_handlers.temp_records.get(1))
        self.assertIsNone(command_handlers.user_record_registration_state.get(1))

    async def test_record_registration(self):
        persistence.get_user_config = Mock(return_value=test_metrics)
        await command_handlers.main_handler(self.update, None)
        # should be called twice:
        # first to inform the user the record has been instantiated, second time to get the first metric
        self.assertEqual(2, self.update.effective_user.get_bot().send_message.call_count)
        # verify the first item has been removed
        self.assertEqual(command_handlers.user_record_registration_state.get(1)[0]['name'], 'energy')


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
            "SEVERELY_DEPRESSED": -3
        },
    },
    {
        "name": "energy",
        "type": "numeric",
        "prompt": "How much energy do you have right now?",
        "range": (1, 11),
    }
]
