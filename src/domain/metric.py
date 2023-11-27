from abc import ABC


class Metric(ABC):
    """
    Provides an abstract base class for the numeric and enum type metrics.
    """
    name: str
    prompt: str

    def __init__(self):
        raise TypeError("This class is not supposed to be instantiated directly. "
                        "Please use subclasses EnumMetric or NumericMetric.")


class EnumMetric:
    values: list[str]

    def __init__(self, name: str, prompt: str, values: list[str]):
        self.name = name
        self.prompt = prompt
        self.values = values


class NumericMetric:
    range: tuple[int, int]

    def __init__(self, name: str, prompt: str, numeric_range: tuple[int, int]):
        self.name = name
        self.prompt = prompt
        self.range = numeric_range


if __name__ == '__main__':
    # examples for instantiation
    mood = EnumMetric(name="mood", prompt="How are you feeling today?", values=["good", "ok", "bad"])
    sleep = NumericMetric(name="sleep", prompt="How many hours did you sleep last night?", numeric_range=(0, 16))
    generic_metric = Metric()
