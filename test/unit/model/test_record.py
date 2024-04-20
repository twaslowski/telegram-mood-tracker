import datetime

import pytest

from src.model.metric import Metric
from src.model.record import Record, TempRecord


@pytest.fixture
def record() -> Record:
    return Record(
        user_id=1,
        data={"metric-1": 1},
        timestamp=datetime.datetime.now(),
    )


@pytest.fixture
def temp_record() -> TempRecord:
    return TempRecord(
        [
            Metric(name="metric-1", user_prompt="metric user prompt", values={"1": 1}),
        ],
    )


def test_next_unanswered_metric(temp_record):
    temp_record.data = {"metric-1": None}
    assert temp_record.next_unanswered_metric().name == "metric-1"


def test_next_unanswered_metric_for_two_unanswered_metrics(temp_record):
    temp_record.data = {"metric-1": None, "metric-2": None}
    assert temp_record.next_unanswered_metric().name == "metric-1"


def test_is_complete(temp_record):
    temp_record.data = {"metric-1": 1}
    assert temp_record.is_complete()


def test_is_not_complete(temp_record):
    temp_record.data = {"metric-1": None}
    assert not temp_record.is_complete()


def test_update_data(temp_record):
    temp_record.update_data("metric-1", 1)
    assert temp_record.data["metric-1"] == 1


def test_update_data_raises_value_error(temp_record):
    with pytest.raises(ValueError):
        temp_record.update_data("unknown-metric", 1)
