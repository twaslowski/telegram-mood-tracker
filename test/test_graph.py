import datetime
import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import src.persistence
from src.handlers.command_handlers import init_user, get_all_months_for_offset


class TestGraph(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        src.persistence.find_oldest_record_for_user = Mock(
            return_value={'record': {
                    'mood': 'NEUTRAL'
                },
                'timestamp': datetime.datetime.now().replace(month=6),
                'user_id': 1})
        self.initialise_user()

    @staticmethod
    def initialise_user():
        update = Mock()
        update.effective_user.id = 1
        init_user(update, None)

    async def test_should_graph_for_correct_months(self):
        self.assertEqual([(2021, 6)], get_all_months_for_offset(1, 2021, 6))
        self.assertEqual([(2021, 4), (2021, 5), (2021, 6)], get_all_months_for_offset(3, 2021, 6))
        self.assertEqual([(2020, 11), (2020, 12), (2021, 1)], get_all_months_for_offset(3, 2021, 1))
