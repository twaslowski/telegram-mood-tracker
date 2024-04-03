import datetime

from pydantic import BaseModel


class AutoBaselineConfig(BaseModel):
    """
    Configuration for the baseline metric.
    """

    enabled: bool
    time: datetime.time
