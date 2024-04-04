import datetime

import pytest

from src.config.auto_baseline import AutoBaselineConfig


def test_auto_baseline_enabled_without_time():
    with pytest.raises(ValueError):
        AutoBaselineConfig(enabled=True, time=None)


def test_disabled_auto_baseline():
    assert AutoBaselineConfig().enabled is False


def test_auto_baseline_parsing_with_time():
    assert AutoBaselineConfig(
        **{"enabled": "true", "time": "00:00"}
    ).time == datetime.time(0, 0)


def test_auto_baseline_parsing_without_time():
    assert AutoBaselineConfig(**{"enabled": "false"}).time is None


def test_dump_with_no_time_configured():
    assert AutoBaselineConfig(enabled=False).model_dump() == {"enabled": False}
