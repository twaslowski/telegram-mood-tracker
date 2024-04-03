import datetime
from typing import Any

from pydantic import BaseModel


class AutoBaselineConfig(BaseModel):
    """
    Configuration for the baseline metric.
    """

    enabled: bool = False
    time: datetime.time | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.enabled and self.time is None:
            raise ValueError("Auto baseline is enabled but no time is defined")

    def model_dump(self, **kwargs):
        return {
            "time": self.time.isoformat(),
            "enabled": self.enabled,
        }
