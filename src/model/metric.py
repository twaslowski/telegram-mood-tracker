from enum import Enum

from pydantic import BaseModel


class MetricType(Enum):
    """
    As of now are two types of metrics: Those that take a numeric range as data and those that have distinct options.
    But really, ultimately we always end up with a fixed range of possible values.
    In the case of an enum, like mood, those values have to map to numbers under the hood, whereas with the
    numeric range we can work with numbers more directly.
    Probably this distinction is introducing unnecessary complexity and should be removed eventually.
    """

    NUMERIC = 0
    ENUM = 1


class Metric(BaseModel):
    name: str
    user_prompt: str
    metric_type: MetricType


class NumericalMetric(Metric):
    metric_type = MetricType.NUMERIC
    data: int


class EnumMetric(Metric):
    metric_type = MetricType.ENUM
    data: Enum
