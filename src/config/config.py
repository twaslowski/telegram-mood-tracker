import logging

import yaml
from pydantic import BaseModel, Field

from typing import Any
from pyautowire import Injectable
from src.config.auto_baseline import AutoBaselineConfig
from src.config.config_metric import ConfigMetric
from src.config.db_config import DatabaseConfig

from src.model.metric import Metric
from src.model.notification import Notification


class Configuration(BaseModel, Injectable):
    metrics: list[ConfigMetric]
    notifications: list[Notification] = []
    auto_baseline: AutoBaselineConfig = Field(default_factory=AutoBaselineConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    def get_metrics(self) -> list[Metric]:
        return [Metric(**metric.model_dump()) for metric in self.metrics]

    def get_notifications(self) -> list[Notification]:
        return self.notifications

    def get_auto_baseline_config(self):
        return self.auto_baseline

    def model_post_init(self, __context: Any) -> None:
        if self.auto_baseline.enabled:
            # check that baselines are defined for all metrics
            for metric in self.metrics:
                assert metric.baseline is not None


class ConfigurationProvider:
    _configuration: Configuration

    def __init__(self, config_file: str = "config.yaml"):
        self.configuration = ConfigurationProvider.load(config_file)

    @staticmethod
    def load(config_file: str) -> Configuration:
        """
        Loads configuration from a YAML file.
        param config_file Path to the YAML configuration file.
        return configuration dictionary with parsed data.
        """
        config = ConfigurationProvider.read_yaml(config_file)
        logging.debug("Raw parsed YAML configuration: %s", config)
        return Configuration(**config)

    @staticmethod
    def read_yaml(config_file: str) -> dict:
        """
        Reads a YAML file.
        param config_file Path to the YAML configuration file.
        return dictionary with parsed data.
        """
        with open(config_file, "r") as stream:
            return yaml.safe_load(stream)

    def get_configuration(self) -> Configuration:
        return self.configuration
