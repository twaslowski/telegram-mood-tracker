import inspect
from kink import di

from src.config import Configuration, ConfigurationProvider
from src.autowiring.injectable import Injectable


def autowire(func):
    """
    Decorator that autowires the parameters of a function.
    Parameters are autowired if they
    - Are of a class that is a subclass of Injectable
    - They exist within kink's dependency injection container
    - They do not possess a default value as per the method signature
    :param func: decorated function
    :return: fully autowired function
    """
    sig = inspect.signature(func)

    def wrapper(*args, **kwargs):
        for name, param in sig.parameters.items():
            if param.default == param.empty and name not in kwargs:  # Check if the parameter has a default value
                param_type = param.annotation
                if inspect.isclass(param_type) and issubclass(param_type, Injectable):
                    fully_qualified_name = param_type.get_fully_qualified_name()
                    if fully_qualified_name in di:
                        kwargs[name] = di[fully_qualified_name]
        return func(*args, **kwargs)

    return wrapper
