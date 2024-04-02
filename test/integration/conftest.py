from unittest.mock import patch

import mongomock
import pytest
from kink import di
from pymongo import MongoClient

from src.repository import record_repository
from src.repository.user_repository import UserRepository


@pytest.fixture(autouse=True)
def patch_user_collection():
    mock_client = mongomock.MongoClient()
    di['mongo_client'] = mock_client
    user_repository = UserRepository(mock_client)
    user_repository.register()


@pytest.fixture(autouse=True)
def patch_records_collection():
    with patch.object(
            record_repository, "records", new=mongomock.MongoClient().db.collection
    ):
        yield
