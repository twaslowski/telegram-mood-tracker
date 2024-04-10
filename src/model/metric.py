from typing import Any

from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    user_prompt: str
    values: dict[str, int]
    baseline: int | None = None

    def model_post_init(self, __context: Any) -> None:
        if self.baseline is not None:
            assert self.baseline in self.values.values()
