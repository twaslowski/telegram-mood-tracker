import kink
import pytest

from src.autowiring.inject import autowire, ParameterNotInCacheError, ParameterNotInSignatureError
from src.autowiring.injectable import Injectable


class SomeClass(Injectable):
    field: str

    def __init__(self, field: str = "some-value"):
        super().__init__()
        self.field = field


def test_trivial_autowiring():
    SomeClass().register()

    @autowire("some_class")
    def test_func(some_class: SomeClass):
        return some_class.field

    assert test_func() == "some-value"


def test_autowiring_with_args():
    SomeClass().register()

    @autowire("some_class")
    def test_func(string: str, some_class: SomeClass):
        return some_class.field + string

    assert test_func("arg") == "some-valuearg"


def test_exception_thrown_when_di_cache_is_empty():
    # the fact that there is no way of unregistering things may be problematic
    kink.di._services = {}

    @autowire("some_class")
    def test_func(some_class: SomeClass):
        return some_class.field

    with pytest.raises(ParameterNotInCacheError):
        test_func()


def test_cache_object_can_be_overwritten():
    @autowire("some_class")
    def test_func(some_class: SomeClass):
        return some_class.field

    kink.di[SomeClass.get_fully_qualified_name()] = SomeClass("new-value")
    assert test_func() == "new-value"


def test_exception_thrown_on_argument_mismatch():
    SomeClass().register()

    @autowire("another_class")
    def test_func(some_class: SomeClass):
        return some_class.field

    with pytest.raises(ParameterNotInSignatureError):
        test_func()
