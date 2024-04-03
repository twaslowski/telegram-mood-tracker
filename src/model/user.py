from pydantic import BaseModel

from src.config.auto_baseline import AutoBaselineConfig
from src.model.metric import Metric
from src.model.notification import Notification


class User(BaseModel):
    user_id: int
    metrics: list[Metric]
    notifications: list[Notification]
    auto_baseline_config: AutoBaselineConfig = AutoBaselineConfig()

    def has_baselines_defined(self) -> bool:
        return all(metric.baseline is not None for metric in self.metrics)

    def has_auto_baseline_enabled(self) -> bool:
        return self.auto_baseline_config.enabled

    def get_auto_baseline_time(self) -> str:
        return self.auto_baseline_config.time
