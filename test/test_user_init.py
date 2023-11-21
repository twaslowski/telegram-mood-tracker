from unittest import TestCase
from unittest.mock import Mock

import src.persistence as persistence
from src.handlers.command_handlers import init_user


class TestUser(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        persistence.user.delete_many({})

    def test_registration(self):
        update = Mock()
        update.effective_user.id = 1
        init_user(update, None)
        user = persistence.user.find_one({"user_id": 1})
        self.assertIsNotNone(user)
        self.assertIsNotNone(user['metrics'])
        self.assertIsNotNone(user['notifications'])

    def test_no_double_registration(self):
        update = Mock()
        update.effective_user.id = 1
        init_user(update, None)
        init_user(update, None)
        users = persistence.user.find({"user_id": 1})
        self.assertEqual(len(list(users)), 1)
