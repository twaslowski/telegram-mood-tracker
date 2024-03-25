import datetime
import logging
import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

from expiringdict import ExpiringDict

import src.handlers.command_handlers as command_handlers
import src.persistence as persistence
from src.handlers.command_handlers import init_record, button, init_user


class TestRecord(IsolatedAsyncioTestCase):
    expiry_time = 3

    async def asyncSetUp(self) -> None:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )

        # set up update object
        self.update = Mock()
        self.update.effective_user.id = 1
        self.update.effective_user.get_bot().send_message = AsyncMock()

        # mock user response to first record
        await self.mock_button_update()

        # mock command handler methods and objects like expiring dicts
        await self.mock_command_handler_methods()

    async def mock_command_handler_methods(self):
        command_handlers.temp_records = ExpiringDict(
            max_len=100, max_age_seconds=self.expiry_time
        )
        command_handlers.state = ExpiringDict(
            max_len=100, max_age_seconds=self.expiry_time
        )
        command_handlers.handle_enum_metric = AsyncMock()
        command_handlers.handle_numeric_metric = AsyncMock()
        command_handlers.handle_no_known_state = AsyncMock()

    async def mock_button_update(self):
        self.button_update = AsyncMock()
        self.button_update.effective_user.id = 1
        mock_bot = AsyncMock()
        self.button_update.effective_user.get_bot = Mock(return_value=mock_bot)
        query = AsyncMock()
        query.data = "NEUTRAL"
        query.message.text = "How do you feel right now?"
        self.button_update.callback_query = query
        mock_bot.send_message = AsyncMock()

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
        time.sleep(self.expiry_time + 1)
        # after being emptied, the dict contains an empty list, as opposed to being empty entirely
        self.assertIsNone(command_handlers.temp_records.get(1))

        # when user attempts to record, they receive an error message
        await command_handlers.button(self.button_update, None)
        command_handlers.handle_no_known_state.called_count = 1

    async def test_record_registration(self):
        """
        Tests the state transition from recording Metric A to Metric B.
        Does not cover the state transition from Metric N to Finished.
        """
        # given
        persistence.get_user_config = Mock(return_value=test_metrics)

        # when /record
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(
            1, self.update.effective_user.get_bot().send_message.call_count
        )
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        # when
        await button(self.button_update, None)

        # then
        # first metric is set in the temporary record
        self.assertEqual(
            command_handlers.temp_records.get(1)["record"]["mood"], "NEUTRAL"
        )
        self.assertEqual(command_handlers.temp_records.get(1)["record"]["energy"], None)
        # in response, the second record is queried
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

    async def test_finish_record_creation(self):
        """
        Tests state transition from recording Metric N to Finished.
        :return:
        """
        persistence.get_user_config = Mock(return_value=test_metrics[:1])

        # when /record
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(
            1, self.update.effective_user.get_bot().send_message.call_count
        )
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        # when
        await button(self.button_update, None)

        # then
        # verify that the temporary record has been cleaned
        self.assertIsNone(command_handlers.temp_records.get(1))

        # verify record was created
        user_records = persistence.find_records_for_user(1)
        self.assertEqual(1, len(user_records))
        self.assertEqual(user_records[0]["record"]["mood"], "NEUTRAL")
        self.assertEqual(datetime.datetime, type(user_records[0]["timestamp"]))

    async def test_double_answer_works_as_intended(self):
        """
        Verify that a user answer the same question works as intended (i.e. the previous record is overwritten).
        Extends `test_record_registration`
        :return:
        """
        # given
        persistence.get_user_config = Mock(return_value=test_metrics)

        # when /record
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(
            1, self.update.effective_user.get_bot().send_message.call_count
        )
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        # when
        await button(self.button_update, None)

        # then
        self.assertEqual(
            command_handlers.temp_records.get(1)["record"]["mood"], "NEUTRAL"
        )
        self.assertEqual(command_handlers.temp_records.get(1)["record"]["energy"], None)

        # given user answers the same question again
        query = AsyncMock()
        query.data = "MODERATELY_ELEVATED"
        query.message.text = "How do you feel right now?"
        self.button_update.callback_query = query

        # when
        await button(self.button_update, None)

        # then
        self.assertEqual(
            command_handlers.temp_records.get(1)["record"]["mood"],
            "MODERATELY_ELEVATED",
        )
        self.assertEqual(command_handlers.temp_records.get(1)["record"]["energy"], None)

    async def test_record_with_offset(self):
        # given
        persistence.get_user_config = Mock(return_value=test_metrics)

        # when /record
        await command_handlers.main_handler(self.update, None)

        # then
        self.assertEqual(
            1, self.update.effective_user.get_bot().send_message.call_count
        )
        self.assertEqual(1, command_handlers.handle_enum_metric.call_count)

        offset_context = Mock()
        offset_context.args = [1]

        # when
        await command_handlers.offset_handler(self.update, offset_context)

        # then
        self.assertEqual(
            datetime.datetime.fromisoformat(
                command_handlers.temp_records.get(1)["timestamp"]
            ).day,
            datetime.datetime.now().day - 1,
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
