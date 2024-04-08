import logging
import os

import boto3
import pymongo
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from src.config.config import ConfigurationProvider, Configuration
from src.handlers.error_handler import error_handler
from src.repository.record_repository import RecordRepository
from src.repository.user_repository import UserRepository
from src.handlers.record_handlers import (
    record_handler,
    button,
    offset_handler,
    baseline_handler,
)
from src.handlers.user_handlers import create_user, toggle_auto_baseline
from src.handlers.graphing import graph_handler
from src.notifier import Notifier
from src.service.user_service import UserService

TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


class MoodTrackerApplication:
    """
    Application superclass.
    Contains and managed the Telegram Application as well as a Notifier.
    """

    def __init__(self, api_token):
        self.application = ApplicationBuilder().token(api_token).build()
        self.initialize_handlers()
        self.initialize_notifier()

    def initialize_notifier(self):
        notifier = Notifier(self.application.job_queue)
        notifier.register()

    def initialize_handlers(self):
        """
        App entrypoint. Defines handlers, schedules reminders.
        :return:
        """
        self.application.add_handler(CommandHandler("start", create_user))
        self.application.add_handler(CommandHandler("graph", graph_handler))
        self.application.add_handler(CommandHandler("record", record_handler))
        self.application.add_handler(CommandHandler("baseline", baseline_handler))
        self.application.add_handler(
            CommandHandler("auto_baseline", toggle_auto_baseline)
        )
        self.application.add_handler(CommandHandler("offset", offset_handler))
        self.application.add_error_handler(error_handler)
        self.application.add_handler(CallbackQueryHandler(button))

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def refresh_user_configs(configuration: Configuration, user_repository: UserRepository):
    """
    Overwrites the user configurations in the database with the configurations in the config file.
    """
    for user in user_repository.find_all_users():
        logging.info(f"Updating user {user.user_id} with new configurations")
        user.metrics = configuration.get_metrics()
        user.notifications = configuration.get_notifications()
        user.auto_baseline_config = configuration.get_auto_baseline_config()
        user_repository.update_user(user)


def initialize_database(
    configuration: Configuration,
) -> tuple[UserRepository, RecordRepository]:
    """
    Initializes the database by creating the tables if they do not exist.
    """
    mongo_client = initialize_mongo_client()

    # Create repositories and register them
    user_repository = UserRepository(mongo_client)
    record_repository = RecordRepository(mongo_client)
    return user_repository.register(), record_repository.register()


def initialize_dynamodb_client():
    """
    Initializes the DynamoDB client.
    """
    dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])


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


def initialize_application() -> MoodTrackerApplication:
    """
    Initializes the application context.
    This means creating all the Singletons in order. There is no auto-generated dependency tree that is followed,
    so this function handles the precise order of initialization. This won't scale well, but it's fine for now.
    :return:
    """
    # Load and register configuration object
    configuration = ConfigurationProvider().get_configuration().register()
    initialize_database(configuration)

    application = MoodTrackerApplication(TOKEN)

    # The Notifier, which is required by the UserService, is now initialized
    user_service = UserService().register()
    user_service.schedule_auto_baselines()
    user_service.schedule_notifications()

    return application


def main():
    application = initialize_application()
    application.run()


if __name__ == "__main__":
    main()
