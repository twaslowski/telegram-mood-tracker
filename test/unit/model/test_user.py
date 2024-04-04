import pytest

from src.config.auto_baseline import AutoBaselineConfig
from src.model.metric import Metric

from src.model.user import User


@pytest.fixture
def metric_with_baseline():
    return Metric(name="test", user_prompt="test", values={"test": 1}, baseline=1)


@pytest.fixture
def metric_without_baseline():
    return Metric(name="test", user_prompt="test", values={"test": 1})


def test_baseline_is_available(metric_with_baseline):
    user = User(user_id=1, metrics=[metric_with_baseline], notifications=[])
    assert user.has_baselines_defined() is True


def test_baseline_is_not_available(metric_without_baseline):
    user = User(user_id=1, metrics=[metric_without_baseline], notifications=[])
    assert user.has_baselines_defined() is False


def test_auto_baseline_is_not_available_by_default(metric_without_baseline):
    user = User(user_id=1, metrics=[metric_without_baseline], notifications=[])
    assert user.has_auto_baseline_enabled() is False


def test_auto_baseline_is_enabled(metric_with_baseline):
    user = User(
        user_id=1,
        metrics=[metric_with_baseline],
        notifications=[],
        auto_baseline_config=AutoBaselineConfig(enabled=True, time="00:00"),
    )
    assert user.has_auto_baseline_enabled() is True


def test_auto_baseline_with_empty_metrics_throws_exception():
    with pytest.raises(ValueError):
        User(
            user_id=1,
            metrics=[],
            notifications=[],
            auto_baseline_config=AutoBaselineConfig(enabled=True, time="00:00"),
        )
