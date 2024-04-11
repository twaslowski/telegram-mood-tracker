import logging

import src.repository.user_repository as user_repository
from src.app import initialize_mongo_client, initialize_dynamodb_client
from src.config.config import ConfigurationProvider
from src.repository.dynamodb.dynamodb_record_repository import DynamoDBRecordRepository
from src.repository.dynamodb.dynamodb_user_repository import DynamoDBUserRepository
from src.repository.mongodb.mongodb_record_repository import MongoDBRecordRepository
from src.repository.mongodb.mongodb_user_repository import MongoDBUserRepository


def migrate_notifications():
    """
    The data structure for metrics and notifications has changed.
    This function migrates the data to the new structure by simply deleting the old user data structure
    and replacing it with the new one. Every user was simply using the defaults anyhow, so no data is lost.
    :return:
    """
    for user in user_repository.user.find():
        user_repository.user.delete_one({"user_id": user["user_id"]})
        user_repository.create_user(user["user_id"])


def migrate_record_format():
    """
    As of 0.4.0, I've racked up a fair bit of tech debt around the data structure of records.
    I'm taking the time to fix this now.
    This function migrates all records to the new format. That means:
    - Any non-int data fields on existing records will be converted to int.
    - The "record" field on records will be renamed to "data"
    :return:
    """
    # Initialize MongoDB
    mongo_client = initialize_mongo_client()
    mongodb_user_repository = MongoDBUserRepository(mongo_client)
    mongodb_record_repository = MongoDBRecordRepository(mongo_client)

    for user in [mongodb_user_repository.find_user(1965256751)]:
        logging.info("Migrating user %s" % user)
        user_records = mongodb_record_repository.find_records_for_user(user.user_id)
        logging.info(
            "Migrating %d records for user %s" % (len(user_records), user.user_id)
        )
        for record in user_records:
            record_dict = record.dict()
            record_dict["data"] = record_dict.pop("record")
            logging.info("Migrating record %s" % record_dict)

            mongodb_record_repository.records.update_one(
                {
                    "user_id": record_dict["user_id"],
                    "timestamp": record_dict["timestamp"],
                },
                {"$set": record_dict, "$unset": {"record": ""}},
            )


def migrate_from_mongodb_to_dynamodb():
    """
    As of 0.4.0, DynamoDB is supported as a persistence backend.
    This function migrates all users from MongoDB to DynamoDB.
    :return:
    """
    configuration = ConfigurationProvider().get_configuration().register()

    # Initialize DynamoDB
    dynamodb = initialize_dynamodb_client("us-east-1")

    dynamodb_user_repository = DynamoDBUserRepository(dynamodb)
    dynamodb_record_repository = DynamoDBRecordRepository(dynamodb)

    # Initialize MongoDB
    mongo_client = initialize_mongo_client()
    mongodb_user_repository = MongoDBUserRepository(mongo_client)
    mongodb_record_repository = MongoDBRecordRepository(mongo_client)

    for user in mongodb_user_repository.find_all_users():
        logging.info("Migrating user %s" % user.user_id)
        dynamodb_user_repository.create_user(user.user_id)
        dynamodb_user_repository.update_user(user)
        user_records = mongodb_record_repository.find_records_for_user(user.user_id)
        logging.info(
            "Migrating %d records for user %s" % (len(user_records), user.user_id)
        )
        for record in user_records:
            dynamodb_record_repository.create_record(
                record.user_id, record.data, record.timestamp
            )
