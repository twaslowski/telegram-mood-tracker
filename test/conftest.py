from unittest.mock import patch

import mongomock
import pytest

from src import persistence


@pytest.fixture(autouse=True)
def patch_user_collection():
    with patch.object(persistence, "user", new=mongomock.MongoClient().db.collection):
        yield


@pytest.fixture(autouse=True)
def patch_records_collection():
    with patch.object(
        persistence, "records", new=mongomock.MongoClient().db.collection
    ):
        yield
