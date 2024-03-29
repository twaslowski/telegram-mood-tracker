import logging
import os
from functools import partial

from dotenv import load_dotenv
from telegram import Update
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
from src.handlers.user_handlers import create_user
from src.handlers.graphing import graph_handler
from src.reminder import reminder

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def init_reminders(app: Application) -> None:
    """
    Adds reminders to the job queue for all users that have configured reminders.
    :param app: The initialised Telegram app object.
    """
    j = app.job_queue
    for user in user_repository.find_all_users():
        user_id = user.user_id
        notifications = user.notifications
        logging.info(f"Setting up notifications for for user {user_id}")
        for notification in notifications:
            reminder_partial = partial(reminder, text=notification.text)
            # __name__ is required by the run_daily() method
            reminder_partial.__name__ = f"reminder_{user_id}_{notification.time}"
            j.run_daily(
                reminder_partial,
                days=(0, 1, 2, 3, 4, 5, 6),
                chat_id=user_id,
                time=notification.time,
            )


def init_app() -> Application:
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
    init_reminders(app)
    return app


if __name__ == "__main__":
    application = init_app()
    logging.info("Starting application")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
