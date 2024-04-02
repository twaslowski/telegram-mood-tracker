import pytest

from src.autowiring.inject import autowire
from src.autowiring.injectable import Injectable


class SomeClass(Injectable):
    field: str

    def __init__(self, field: str = "some-value"):
        super().__init__()
        self.field = field


@pytest.fixture(autouse=True)
def setup():
    SomeClass().register()


def test_trivial_autowiring():
    @autowire("test_class")
    def test_func(test_class: SomeClass):
        return test_class.field

    assert test_func() == "some-value"


def test_autowiring_with_args():
    @autowire("test_class")
    def test_func(string: str, test_class: SomeClass):
        return test_class.field + string

    assert test_func(string="arg") == "some-valuearg"
