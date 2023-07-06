from dataclasses import dataclass
from src.data.mood import Mood
from src.data.numeric_metric import NumericMetric
from src.data.appetite import Appetite


@dataclass
class MoodRecord:
    mood: Mood = None
    appetite: Appetite = None
    energy: NumericMetric = None
    sleep: NumericMetric = None
    anxiety: NumericMetric = None
    back_pain: NumericMetric = None
