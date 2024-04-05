import datetime

import pytest

from src.model.metric import Metric
from src.model.record import Record, RecordData, TempRecord


@pytest.fixture
def record() -> Record:
    return Record(
        user_id=1,
        data=[
            RecordData(metric_name="metric1", value=1),
        ],
        timestamp=datetime.datetime.now(),
    )


@pytest.fixture
def temp_record() -> TempRecord:
    return TempRecord(
        metrics=[
            Metric(name="metric1", user_prompt="metric user prompt", values={"1": 1}),
        ],
    )


def test_find_existing_record_data_in_record(record: Record):
    assert record.find_record_data_by_name("metric1").value == 1


def test_find_non_existing_data_in_record(record: Record):
    assert record.find_record_data_by_name("metric2") is None


def test_find_existing_metric_in_temp_record(temp_record: TempRecord):
    assert temp_record.find_metric_by_name("metric1").name == "metric1"


def test_find_non_existing_metric_in_temp_record(temp_record: TempRecord):
    assert temp_record.find_metric_by_name("metric2") is None
