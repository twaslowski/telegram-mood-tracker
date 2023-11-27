from typing import Union


class MetricEntry:
    """
    A metric entry is a single metric and its value. It is a single data point in a record.
    """
    metric_name: str
    value: Union[str, int]


class Record:
    """
    A record is a collection of metrics and their values. It is a snapshot of a user's health at a given point in
    time.
    """

    user_id: int
    timestamp: str
    metrics: list[MetricEntry]

    def __init__(self, user_id: int, timestamp: str, metrics: list[MetricEntry]):
        self.user_id = user_id
        self.timestamp = timestamp
        self.metrics = metrics
