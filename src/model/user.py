import datetime
from typing import Any

from pydantic import BaseModel

from src.config.auto_baseline import AutoBaselineConfig
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

    def enable_auto_baseline(self) -> None:
        self.auto_baseline_config.enabled = True

    def get_metrics_without_baselines(self) -> list[str]:
        return [metric.name for metric in self.metrics if metric.baseline is None]

    def has_baselines_defined(self) -> bool:
        return self.metrics != [] and all(
            metric.baseline is not None for metric in self.metrics
        )

    def has_auto_baseline_enabled(self) -> bool:
        return self.auto_baseline_config.enabled

    def get_auto_baseline_time(self) -> datetime.time:
        return self.auto_baseline_config.time
