import logging
import os

import pymongo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

from src.config import ConfigurationProvider, Configuration
from src.repository.record_repository import RecordRepository
from src.repository.user_repository import UserRepository
from src.autowiring.inject import autowire
from src.handlers.record_handlers import (
    record_handler,
    button,
    offset_handler,
)
from src.handlers.user_handlers import create_user
from src.handlers.graphing import graph_handler
from src.notifier import Notifier

TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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
        self.application.add_handler(CommandHandler("offset", offset_handler))
        self.application.add_handler(CallbackQueryHandler(button))

    def run(self):
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    @autowire("notifier", "user_repository")
    def initialize_notifications(
        self, notifier: Notifier, user_repository: UserRepository
    ) -> None:
        """
        Adds reminders to the job queue for all users that have configured reminders.
        """
        for user in user_repository.find_all_users():
            user_id = user.user_id
            notifications = user.notifications
            logging.info(f"Setting up notifications for for user {user_id}")
            for notification in notifications:
                notifier.set_notification(user_id, notification)


@autowire("configuration", "user_repository")
def refresh_user_configs(configuration: Configuration, user_repository: UserRepository):
    """
    Overwrites the user configurations in the database with the configurations in the config file.
    """
    for user in user_repository.find_all_users():
        logging.info(f"Updating user {user.user_id} with new configurations")
        user_repository.update_user_metrics(user.user_id, configuration.get_metrics())
        user_repository.update_user_notifications(
            user.user_id, configuration.get_notifications()
        )


def initialize_database():
    """
    Initializes the database by creating the tables if they do not exist.
    """
    mongo_client = pymongo.MongoClient(os.environ.get("MONGO_HOST"))
    user_repository = UserRepository(mongo_client)
    record_repository = RecordRepository(mongo_client)
    user_repository.register()
    record_repository.register()


def main():
    # Load and register configuration object
    ConfigurationProvider().get_configuration().register()
    initialize_database()
    # Create application
    refresh_user_configs()
    application = MoodTrackerApplication(TOKEN)
    application.run()


if __name__ == "__main__":
    main()
