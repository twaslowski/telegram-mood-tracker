from kink import di


class Injectable:
    @classmethod
    def get_fully_qualified_name(cls):
        return f"{cls.__module__}.{cls.__name__}"

    def __init__(self):
        di[self.get_fully_qualified_name()] = self
        super().__init__()
