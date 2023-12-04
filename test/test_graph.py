import logging
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock

import src.persistence
from src.handlers.command_handlers import init_user
import src.persistence as persistence


class TestGraph(IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        src.persistence.find_oldest_record_for_user = Mock(return_value={'timestamp': '2021-01-01T00:00:00.000000'})
        self.initialise_user()

    @staticmethod
    def initialise_user():
        update = Mock()
        update.effective_user.id = 1
        init_user(update, None)

    async def test_graph(self):
        self.assertTrue(True)
