import yaml

from src.model.metric import Metric, ConfigMetric
from src.model.notification import Notification


def load_metrics() -> list[Metric]:
    # todo there is a better way to do this
    config = load_config("config.yaml")
    return [
        Metric(**ConfigMetric(**metric).model_dump()) for metric in config["metrics"]
    ]


def load_notifications() -> list[Notification]:
    config = load_config("config.yaml")
    return [Notification(**reminder) for reminder in config["notifications"]]


def load_config(config_file: str) -> dict:
    """
    Loads configuration from a YAML file.
    param config_file Path to the YAML configuration file.
    return configuration dictionary with parsed data.
    """
    with open(config_file, "r") as stream:
        data = yaml.safe_load(stream)
        return data
