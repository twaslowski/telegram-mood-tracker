from typing import Any

import emoji
from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    user_prompt: str
    values: dict[str, int]
    baseline: int | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.baseline is not None:
            assert self.baseline in self.values.values()


def get_value(self, key: str) -> int:
    return self.values[key]
