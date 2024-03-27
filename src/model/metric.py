from typing import Any

import emoji
from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    user_prompt: str
    values: dict[str, int]


def get_value(self, key: str) -> int:
    return self.values[key]


class ConfigMetric(BaseModel):
    """
    Superclass of the Metric class to parse the configuration and perform post-initialization logic.
    Technically, this could probably all be performed within the Metric class itself, but this separates concerns.
    """

    name: str
    user_prompt: str
    values: dict[str, int]
    type: str | None = "enum"
    emoji: bool = False

    def model_post_init(self, __context: Any) -> None:
        if self.type == "numeric":
            assert "lower_bound" in self.values
            assert "upper_bound" in self.values
            self.values = {
                str(i): i
                for i in range(
                    self.values["lower_bound"], self.values["upper_bound"] + 1
                )
            }

        if self.emoji:
            self.values = {emoji.emojize(k): v for k, v in self.values.items()}
