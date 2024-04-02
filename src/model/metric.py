from typing import Any

import emoji
from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    user_prompt: str
    values: dict[str, int]


def get_value(self, key: str) -> int:
    return self.values[key]
