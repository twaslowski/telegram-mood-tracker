from datetime import datetime, timedelta

from copy import deepcopy

import pytest

from src.model.record import Record
import src.visualise as visualize

from pathlib import Path


@pytest.fixture
def user(user_service):
    return user_service.create_user(1)


@pytest.fixture
def record(user):
    return Record(
        user_id=1,
        timestamp=datetime(2022, 3, 2),
        data={metric.name: metric.baseline for metric in user.metrics},
    )


def test_should_retrieve_one_record_for_time_range(record, repositories):
    # Given two records for user 1
    record_days_past = deepcopy(record)
    record_days_future = deepcopy(record)
    record_years_past = deepcopy(record)
    record_years_future = deepcopy(record)

    record_days_past.timestamp = datetime.today() - timedelta(days=10)
    record_days_future.timestamp = datetime.today() + timedelta(days=30)
    record_years_future.timestamp = datetime.today() + timedelta(days=365)
    record_years_past.timestamp = datetime.today() - timedelta(days=365)

    repositories.record_repository.save_record(record)
    repositories.record_repository.save_record(record_days_past)
    repositories.record_repository.save_record(record_days_future)
    repositories.record_repository.save_record(record_years_past)
    repositories.record_repository.save_record(record_years_future)

    # When retrieving records for the last 7 days
    records = visualize.retrieve_records(
        1, record_repository=repositories.record_repository, month=(2022, 3)
    )

    # Then only the record within the time range should be returned
    assert len(records) == 1
    assert records[0].timestamp == record.timestamp


def test_visualize_creates_graph(record):
    # Given a record
    records = [record]

    # When visualizing the record
    graph_path = visualize.visualize(records, (2022, 3))

    # Then the graph should be created
    assert graph_path is not None
    assert graph_path.endswith(".jpg")

    assert "2022" in graph_path
    assert "3" in graph_path

    assert Path(graph_path).exists()
    # Path(graph_path).unlink()  # Clean up
