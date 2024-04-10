import os

import pytest

from pymongo.errors import ServerSelectionTimeoutError
from src.app import initialize_database


def test_non_existent_mongo_host_times_out(configuration):
    os.environ["MONGODB_HOST"] = "255.255.255.255:27017"
    with pytest.raises(ServerSelectionTimeoutError):
        initialize_database(configuration)
