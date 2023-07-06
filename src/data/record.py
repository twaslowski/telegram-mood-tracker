from dataclasses import dataclass
from mood import Mood
from numeric_metric import NumericMetric
from src.data.appetite import Appetite


@dataclass
class MoodRecord:
    mood: Mood
    appetite: Appetite
    energy: NumericMetric
    sleep: NumericMetric
    anxiety: NumericMetric
    back_pain: NumericMetric
