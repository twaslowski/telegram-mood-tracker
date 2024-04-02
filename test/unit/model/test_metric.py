import pytest

from src.model.metric import Metric


def test_baseline_in_existing_values():
    metric = Metric(name="test", user_prompt="test", values={"test": 1}, baseline=1)
    assert metric.baseline == 1


def test_throws_if_baseline_not_in_values():
    with pytest.raises(ValueError):
        Metric(name="test", user_prompt="test", values={"test": 2}, baseline=1)
