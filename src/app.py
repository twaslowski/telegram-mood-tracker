import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, Application, CommandHandler, CallbackQueryHandler

import src.persistence as persistence
from src.handlers.command_handlers import main_handler, button, graph_handler, init_user
from src.reminder import reminder

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="log")


def init_reminders(app: Application) -> None:
    j = app.job_queue
    for user_notification_configuration in persistence.get_all_user_notifications().items():
        for notification_time in user_notification_configuration[1]:
            j.run_daily(reminder, days=(0, 1, 2, 3, 4, 5, 6), chat_id=user_notification_configuration[0],
                        time=notification_time)


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", init_user))
    app.add_handler(CommandHandler("graph", graph_handler))
    app.add_handler(CommandHandler("record", main_handler))
    app.add_handler(CallbackQueryHandler(button))
    init_reminders(app)
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
