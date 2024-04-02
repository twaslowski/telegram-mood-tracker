import inspect
from kink import di

from src.autowiring.injectable import Injectable


class ParameterNotInSignatureError(Exception):
    def __init__(self, parameter):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' specified in @autowire is not in the function signature"
        super().__init__(self.message)


class ParameterNotInCacheError(Exception):
    def __init__(self, parameter):
        self.parameter = parameter
        self.message = f"Parameter '{self.parameter}' does not exist in the 'di' cache"
        super().__init__(self.message)


def autowire(*autowire_params):
    """
    Decorator that autowires the specified parameters of a function.
    Parameters are autowired if they
    - Are specified in the decorator arguments
    - Are of a class that is a subclass of Injectable
    - They exist within kink's dependency injection container
    :param autowire_params: names of parameters to autowire
    :return: fully autowired function
    """

    def decorator(func):
        sig = inspect.signature(func)

        def wrapper(*args, **kwargs):
            for (
                name
            ) in autowire_params:  # Check if the parameter is in the autowire list
                if name not in sig.parameters:
                    raise ParameterNotInSignatureError(name)
                param = sig.parameters[name]
                param_type = param.annotation
                if inspect.isclass(param_type) and issubclass(param_type, Injectable):
                    fully_qualified_name = param_type.get_fully_qualified_name()
                    if fully_qualified_name not in di:
                        raise ParameterNotInCacheError(fully_qualified_name)
                    kwargs[name] = di[fully_qualified_name]
            return func(*args, **kwargs)

        return wrapper

    return decorator
