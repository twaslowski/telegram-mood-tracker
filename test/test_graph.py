import datetime
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock

import src.repository.persistence
from src.handlers.command_handlers import init_user, get_all_months_for_offset


class TestGraph(IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        src.repository.persistence.find_oldest_record_for_user = Mock(
            return_value={
                "record": {"mood": "NEUTRAL"},
                "timestamp": datetime.datetime.now().replace(month=6),
                "user_id": 1,
            }
        )
        await self.initialise_user()

    @staticmethod
    async def initialise_user():
        update = AsyncMock()
        update.effective_user.id = 1
        update.effective_user.get_bot = Mock(return_value=AsyncMock())
        await init_user(update, None)

    async def test_should_graph_for_correct_months(self):
        self.assertEqual([(2021, 6)], get_all_months_for_offset(1, 2021, 6))
        self.assertEqual(
            [(2021, 4), (2021, 5), (2021, 6)], get_all_months_for_offset(3, 2021, 6)
        )
        self.assertEqual(
            [(2020, 11), (2020, 12), (2021, 1)], get_all_months_for_offset(3, 2021, 1)
        )
