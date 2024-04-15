from datetime import datetime, timedelta

from copy import deepcopy
from unittest.mock import Mock, AsyncMock

import pytest

from src.handlers import graphing
from src.model.metric import Metric
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


@pytest.fixture
def month():
    return visualize.Month(2022, 3)


@pytest.fixture
def graph_spec_button():
    # mock button update
    button_update = AsyncMock()
    button_update.effective_user.id = 1
    # mock user response to first record
    mock_bot = AsyncMock()
    button_update.effective_user.get_bot = Mock(return_value=mock_bot)
    query = AsyncMock()
    button_update.callback_query = query
    mock_bot.send_photo = AsyncMock()
    return button_update


def test_should_retrieve_one_record_for_time_range(month, record, repositories):
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
        1, month, record_repository=repositories.record_repository
    )

    # Then only the record within the time range should be returned
    assert len(records) == 1
    assert records[0].timestamp == record.timestamp


def test_visualize_creates_graph(record, repositories, user, month):
    # Given a record
    repositories.record_repository.save_record(record)

    # When visualizing the record
    graph_path = visualize.visualize(user, month)

    # Then the graph should be created
    assert graph_path is not None
    assert graph_path.endswith(".jpg")
    assert Path(graph_path).exists()

    assert "2022" in graph_path
    assert "3" in graph_path

    Path(graph_path).unlink()  # Clean up


@pytest.mark.asyncio
async def test_visualization_end_to_end(graph_spec_button, record, repositories):
    graphing.get_month_tuples_for_time_range = Mock(
        return_value=[visualize.Month(2022, 3)]
    )

    # Given a record
    repositories.record_repository.save_record(record)

    # When visualizing the record
    paths = await graphing.handle_graph_specification(graph_spec_button)

    # Then the graph should be created
    assert graph_spec_button.effective_user.get_bot().send_photo.called
    assert len(paths) == 1
    assert Path(paths[0]).exists()
    assert "2022" in paths[0]
    assert "mood" in paths[0]
    assert "sleep" in paths[0]


@pytest.mark.asyncio
async def test_visualization_for_different_metrics(
    graph_spec_button, record, repositories, user
):
    # Given a user with different metrics
    user.metrics = [
        Metric(name="some-metric", user_prompt="Some metric", values={"10": 10})
    ]
    repositories.user_repository.update_user(user)

    # And a corresponding record
    record.data = {"some-metric": "8"}
    repositories.record_repository.save_record(record)

    # When visualizing the record for a specified time range
    graphing.get_month_tuples_for_time_range = Mock(
        return_value=[visualize.Month(2022, 3)]
    )
    paths = await graphing.handle_graph_specification(graph_spec_button)

    # Then the graph should be created
    assert graph_spec_button.effective_user.get_bot().send_photo.called

    assert len(paths) == 1
    assert Path(paths[0]).exists()
    assert "some-metric" in paths[0]
