import pytest
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
