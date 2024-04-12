import logging
import os

import boto3
import pymongo

from src.config.config import Configuration
from src.repository.dynamodb.dynamodb_record_repository import DynamoDBRecordRepository
from src.repository.dynamodb.dynamodb_user_repository import DynamoDBUserRepository
from src.repository.mongodb.mongodb_record_repository import MongoDBRecordRepository
from src.repository.mongodb.mongodb_user_repository import MongoDBUserRepository
from src.repository.record_repository import RecordRepository
from src.repository.user_repository import UserRepository


def initialize_database(
    configuration: Configuration,
) -> tuple[UserRepository, RecordRepository]:
    """
    Initializes the database by creating the tables if they do not exist.
    """
    if configuration.database.type == "dynamodb":
        dynamodb = initialize_dynamodb_client(configuration.database.aws_region)

        user_repository = DynamoDBUserRepository(dynamodb)
        record_repository = DynamoDBRecordRepository(dynamodb)
    else:
        mongo_client = initialize_mongo_client()

        # Create repositories and register them
        user_repository = MongoDBUserRepository(mongo_client)
        record_repository = MongoDBRecordRepository(mongo_client)

    return user_repository.register(
        alias="user_repository"
    ), record_repository.register(alias="record_repository")


def initialize_dynamodb_client(aws_region: str) -> boto3.resource:
    """
    Initializes the DynamoDB client.
    """
    dynamodb = boto3.resource("dynamodb", region_name=aws_region)
    logging.info(
        f"Successfully established connection to DynamoDB persistence backend in region {aws_region}."
    )
    return dynamodb


def initialize_mongo_client() -> pymongo.MongoClient:
    """
    Initializes the MongoDB client.
    """
    client = pymongo.MongoClient(
        os.environ.get("MONGODB_HOST"), ServerSelectionTimeoutMS=5000
    )
    client.server_info()
    logging.info("Successfully established connection to MongoDB persistence backend.")
    return client
