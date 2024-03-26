from enum import Enum

from expiringdict import ExpiringDict

APPLICATION_STATE = ExpiringDict(max_len=100, max_age_seconds=300)


class State(Enum):
    RECORDING = 1
    GRAPHING = 2
