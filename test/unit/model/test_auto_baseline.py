import pytest

from src.config.auto_baseline import AutoBaselineConfig


def test_auto_baseline_enabled_without_time():
    with pytest.raises(ValueError):
        AutoBaselineConfig(enabled=True, time=None)


def test_disabled_auto_baseline():
    assert AutoBaselineConfig().enabled is False
