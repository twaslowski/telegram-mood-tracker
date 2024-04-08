from typing import Any

from pydantic import BaseModel, field_validator


class DatabaseConfig(BaseModel):
    database_type: str = "mongodb"
    aws_region: str | None = None

    @field_validator("database_type")
    @classmethod
    def validate_database_type(cls, value: str):
        value = value.lower()
        if value not in ["mongodb", "dynamodb"]:
            raise ValueError("Database type must be either mongodb or mysql")
        return value

    def model_post_init(self, __context: Any) -> None:
        if self.database_type == "dynamodb":
            assert self.aws_region is not None
