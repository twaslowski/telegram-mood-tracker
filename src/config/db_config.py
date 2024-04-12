from typing import Any

from pydantic import BaseModel, field_validator


class DatabaseConfig(BaseModel):
    type: str = "mongodb"
    aws_region: str | None = None

    @field_validator("type")
    @classmethod
    def validate_database_type(cls, value: str):
        if value not in ["mongodb", "dynamodb"]:
            raise ValueError("Database type must be either mongodb or dynamodb")
        return value

    def model_post_init(self, __context: Any) -> None:
        if self.type == "dynamodb" and self.aws_region is None:
            raise ValueError("AWS region must be provided for DynamoDB database type")
