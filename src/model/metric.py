from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    user_prompt: str
    values: dict[str, int]
