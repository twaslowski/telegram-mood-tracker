import datetime
import json
from typing import Any

from pydantic import BaseModel

from src.config.auto_baseline import AutoBaselineConfig
from src.config.config import Configuration
from src.model.metric import Metric
from src.model.notification import Notification


class User(BaseModel):
    user_id: int
    metrics: list[Metric]
    notifications: list[Notification]
    auto_baseline_config: AutoBaselineConfig = AutoBaselineConfig()

    def model_post_init(self, __context: Any) -> None:
        if self.has_auto_baseline_enabled() and not self.has_baselines_defined():
            raise ValueError("Auto baseline is enabled but no baselines are defined")

    def get_notifications(self) -> list[Notification]:
        return self.notifications

    def enable_auto_baseline(self) -> None:
        self.auto_baseline_config.enabled = True

    def disable_auto_baseline(self) -> None:
        self.auto_baseline_config.enabled = False

    def get_metrics_without_baselines(self) -> list[str]:
        return [
            metric.name.capitalize()
            for metric in self.metrics
            if metric.baseline is None
        ]

    def has_baselines_defined(self) -> bool:
        return self.metrics != [] and all(
            metric.baseline is not None for metric in self.metrics
        )

    def has_auto_baseline_enabled(self) -> bool:
        return self.auto_baseline_config.enabled

    def get_auto_baseline_time(self) -> datetime.time:
        return self.auto_baseline_config.time

    def get_metric_by_name(self, name: str) -> Metric | None:
        for metric in self.metrics:
            if metric.name == name:
                return metric
        return None

    def serialize(self) -> dict:
        # Pydantic's model_dump does not work recursively on subclasses. This performs a complete serialization of the
        # object with a subsequen json.loads() deserialization. Likely compute-inefficient, but throughput is not the
        # main challenge here.
        return json.loads(self.model_dump_json())

    @classmethod
    def from_defaults(cls, user_id: int, configuration: Configuration) -> "User":
        return cls(
            user_id=user_id,
            metrics=[metric.model_dump() for metric in configuration.get_metrics()],
            notifications=[
                notification.model_dump()
                for notification in configuration.get_notifications()
            ],
            auto_baseline_config=configuration.get_auto_baseline_config().model_dump(),
        )
