from unittest import TestCase

from src.domain.metric import Metric, EnumMetric, NumericMetric


class TestMetric(TestCase):

    def test_cannot_instantiate_metric(self):
        with self.assertRaises(TypeError):
            Metric()

    def test_instantiate_enum_metric(self):
        mood = EnumMetric(name="mood", prompt="How are you feeling today?", values=["good", "ok", "bad"])
        self.assertEqual(mood.name, "mood")
        self.assertEqual(mood.prompt, "How are you feeling today?")
        self.assertEqual(mood.values, ["good", "ok", "bad"])

    def test_instantiate_numeric_metric(self):
        sleep = NumericMetric(name="sleep", prompt="How many hours did you sleep last night?", numeric_range=(0, 24))
        self.assertEqual(sleep.name, "sleep")
        self.assertEqual(sleep.prompt, "How many hours did you sleep last night?")
        self.assertEqual(sleep.range, (0, 24))
