import os

import pytest

from pymongo.errors import ServerSelectionTimeoutError
from src.app import initialize_database


def test_non_existent_mongo_host_times_out():
    os.environ["MONGODB_HOST"] = "255.255.255.255:27017"
    with pytest.raises(ServerSelectionTimeoutError):
        initialize_database()


def test_unset_mongo_host_times_out():
    del os.environ["MONGODB_HOST"]
    with pytest.raises(ServerSelectionTimeoutError):
        initialize_database()