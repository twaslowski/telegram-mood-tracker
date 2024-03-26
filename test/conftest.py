from unittest.mock import patch

import mongomock
import pytest

from src.repository import user_repository, record_repository


@pytest.fixture(autouse=True)
def patch_user_collection():
    with patch.object(user_repository, "user", new=mongomock.MongoClient().db.collection):
        yield


@pytest.fixture(autouse=True)
def patch_records_collection():
    with patch.object(
            record_repository, "records", new=mongomock.MongoClient().db.collection
    ):
        yield
