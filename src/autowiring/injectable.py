import logging

from kink import di


class Injectable:
    @classmethod
    def get_fully_qualified_name(cls):
        return f"{cls.__module__}.{cls.__name__}"

    def register(self):
        logging.info(f"Registering {self.get_fully_qualified_name()} as singleton.")
        di[self.get_fully_qualified_name()] = self
