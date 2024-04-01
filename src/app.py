import logging
import os

from dotenv import load_dotenv
from telegram import Update
from kink import di
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    CallbackQueryHandler,
)

import src.repository.user_repository as user_repository
from src.handlers.record_handlers import (
    record_handler,
    button,
    offset_handler,
)
from src.config import configuration
from src.handlers.user_handlers import create_user
from src.handlers.graphing import graph_handler
from src.reminder import Notifier

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def init_notifications(app: Application) -> None:
    """
    Adds reminders to the job queue for all users that have configured reminders.
    :param app: The initialised Telegram app object.
    """
    job_queue = app.job_queue
    for user in user_repository.find_all_users():
        user_id = user.user_id
        notifications = user.notifications
        logging.info(f"Setting up notifications for for user {user_id}")
        for notification in notifications:
            notifier.set_notification(user_id, notification)


def initialize_application() -> Application:
    """
    App entrypoint. Defines handlers, schedules reminders.
    :return:
    """
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", create_user))
    app.add_handler(CommandHandler("graph", graph_handler))
    app.add_handler(CommandHandler("record", record_handler))
    app.add_handler(CommandHandler("offset", offset_handler))
    app.add_handler(CallbackQueryHandler(button))
    return app


def refresh_user_configs():
    """
    Overwrites the user configurations in the database with the configurations in the config file.
    """
    for user in user_repository.find_all_users():
        logging.info(f"Updating user {user.user_id} with new configurations")
        user_repository.update_user_metrics(user.user_id, configuration.get_metrics())
        user_repository.update_user_notifications(user.user_id, configuration.get_notifications())


def initialize_notifier():
    notifier = Notifier(application.job_queue)
    di[Notifier] = notifier
    return notifier


if __name__ == "__main__":
    # todo: this initialization logic does not work well with tests.
    refresh_user_configs()
    application = initialize_application()
    notifier = initialize_notifier()
    logging.info("Starting application")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
