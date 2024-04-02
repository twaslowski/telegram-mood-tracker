import pytest

from src.config import ConfigurationProvider, Configuration


@pytest.fixture
def complete_config() -> dict:
    return ConfigurationProvider.read_yaml("test/resources/config.test.yaml")


def test_baselines_happy_path(complete_config):
    configuration = Configuration(**complete_config)
    assert configuration.baseline.enabled
    for metric in configuration.metrics:
        assert metric.baseline is not None


def test_throw_exception_if_baseline_is_enabled_but_not_set(complete_config):
    complete_config['metrics'][0]['baseline'] = None
    with pytest.raises(Exception):
        Configuration(**complete_config)


def test_throw_exception_if_emojis_are_enabled_for_numeric_metric(complete_config):
    complete_config['metrics'][1]['emoji'] = True  # [1] is sleep, a numeric metric
    with pytest.raises(Exception):
        Configuration(**complete_config)


def test_throw_exception_if_metric_type_is_invalid(complete_config):
    complete_config['metrics'][0]['type'] = 'invalid'
    with pytest.raises(Exception):
        Configuration(**complete_config)


def test_generate_correct_range_for_numeric_metric(complete_config):
    complete_config['metrics'][1]['values']['lower_bound'] = 0
    complete_config['metrics'][1]['values']['upper_bound'] = 10
    configuration = Configuration(**complete_config)
    assert len(configuration.metrics[1].values) == 11  # 0-10 inclusive
