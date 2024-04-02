import yaml
from pydantic import BaseModel

from src.autowiring.injectable import Injectable
from src.model.metric import Metric, ConfigMetric
from src.model.notification import Notification


class Configuration(BaseModel, Injectable):
    metrics: list[ConfigMetric]
    notifications: list[Notification]

    def get_metrics(self) -> list[Metric]:
        return [Metric(**metric.model_dump()) for metric in self.metrics]

    def get_notifications(self) -> list[Notification]:
        return self.notifications


class ConfigurationProvider:
    _configuration: Configuration

    def __init__(self):
        self.configuration = ConfigurationProvider.load("config.yaml")

    @staticmethod
    def load(config_file: str) -> Configuration:
        """
        Loads configuration from a YAML file.
        param config_file Path to the YAML configuration file.
        return configuration dictionary with parsed data.
        """
        with open(config_file, "r") as stream:
            data = yaml.safe_load(stream)
            return Configuration(**data)

    def get_configuration(self) -> Configuration:
        return self.configuration


_configuration = ConfigurationProvider().configuration
