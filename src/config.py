import yaml
from pydantic import BaseModel, field_validator

from typing import Any
import emoji
from src.autowiring.injectable import Injectable
from src.model.metric import Metric
from src.model.notification import Notification


class Configuration(BaseModel, Injectable):
    metrics: list["ConfigMetric"]
    notifications: list[Notification]
    baseline: "BaselineConfig"

    def get_metrics(self) -> list[Metric]:
        return [Metric(**metric.model_dump()) for metric in self.metrics]

    def get_notifications(self) -> list[Notification]:
        return self.notifications

    def model_post_init(self, __context: Any) -> None:
        if self.baseline.enabled:
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
        return Configuration(**ConfigurationProvider.read_yaml(config_file))

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


class ConfigMetric(BaseModel):
    """
    Superclass of the Metric class to parse the configuration and perform post-initialization logic.
    Technically, this could probably all be performed within the Metric class itself, but this separates concerns.
    """

    name: str
    user_prompt: str
    values: dict[str, int]
    baseline: int | None = None
    type: str | None = "enum"
    emoji: bool = False

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            assert v in ["enum", "numeric"]
        return v

    def model_post_init(self, __context: Any) -> None:
        if self.type == "numeric":
            assert "lower_bound" in self.values
            assert "upper_bound" in self.values
            assert self.emoji is False
            self.values = {
                str(i): i
                for i in range(
                    self.values["lower_bound"], self.values["upper_bound"] + 1
                )
            }

        if self.emoji:
            self.values = {emoji.emojize(k): v for k, v in self.values.items()}


class BaselineConfig(BaseModel):
    """
    Configuration for the baseline metric.
    """

    enabled: bool
    auto: bool
