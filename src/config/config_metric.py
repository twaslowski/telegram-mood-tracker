from typing import Any

import emoji
from pydantic import BaseModel, field_validator


class ConfigMetric(BaseModel):
    """
    Superclass of the Metric class to parse the configuration and perform post-initialization logic.
    Technically, this could probably all be performed within the Metric class itself, but this separates concerns.
    """

    name: str
    user_prompt: str
    values: dict[str, int]
    baseline: int | None = None
    type: str | None = "enum"
    emoji: bool = False

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is not None:
            assert v in ["enum", "numeric"]
        return v

    def model_post_init(self, __context: Any) -> None:
        if self.type == "numeric":
            assert "lower_bound" in self.values
            assert "upper_bound" in self.values
            assert self.emoji is False
            self.values = {
                str(i): i
                for i in range(
                    self.values["lower_bound"], self.values["upper_bound"] + 1
                )
            }

        if self.emoji:
            self.values = {emoji.emojize(k): v for k, v in self.values.items()}
