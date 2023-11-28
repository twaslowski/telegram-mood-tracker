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

    async def asyncTearDown(self) -> None:
        persistence.user.delete_many({})
        persistence.records.delete_many({})

    async def test_init_and_invalidate_record(self):
        # create record
        persistence.get_user_config = Mock(return_value=test_metrics)
        await init_user(self.update, None)
        init_record(1)
        self.assertIsNotNone(command_handlers.temp_records.get(1))
        # let expiry time elapse
        time.sleep(6)
        # after being emptied, the dict contains an empty list, as opposed to being empty entirely
        self.assertIsNone(command_handlers.temp_records.get(1))

    async def test_record_registration(self):
        """
        Tests the state transition from recording Metric A to Metric B.
        Does not cover the state transition from Metric N to Finished.
        """
        # given
        persistence.get_user_config = Mock(return_value=test_metrics)
        command_handlers.handle_enum_metric = AsyncMock()
        command_handlers.handle_numeric_metric = AsyncMock()

        # when
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(1, self.update.effective_user.get_bot().send_message.call_count)
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        # user answers first question
        # given
        button_update = AsyncMock()
        button_update.effective_user.id = 1
        query = AsyncMock()
        query.data = 'NEUTRAL'
        button_update.callback_query = query

        # when
        await command_handlers.button(button_update, None)

        # then
        # first metric is set in the temporary record
        self.assertEqual(command_handlers.temp_records.get(1)['record']['mood'], 'NEUTRAL')
        # in response, the second record is queried
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

    async def test_finish_record_creation(self):
        """
        Tests state transition from recording Metric N to Finished.
        :return:
        """
        persistence.get_user_config = Mock(return_value=test_metrics[:1])
        command_handlers.handle_enum_metric = AsyncMock()

        # when
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(1, self.update.effective_user.get_bot().send_message.call_count)
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        # user answers first question
        # given
        button_update = AsyncMock()
        button_update.effective_user.id = 1

        # Mock get_bot to return a mock bot object
        mock_bot = AsyncMock()
        button_update.effective_user.get_bot = Mock(return_value=mock_bot)

        # Since send_message is async, use AsyncMock for it
        mock_bot.send_message = AsyncMock()

        # define query result
        query = AsyncMock()
        query.data = 'NEUTRAL'
        button_update.callback_query = query

        # when
        await command_handlers.button(button_update, None)

        # then
        # verify that the temporary record has been cleaned
        self.assertIsNone(command_handlers.temp_records.get(1))

        # verify record was created
        user_records = persistence.find_records_for_user(1)
        self.assertEqual(1, len(user_records))
        self.assertEqual(user_records[0]['record']['mood'], 'NEUTRAL')


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