import os
import logging
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder, Application, CommandHandler, CallbackQueryHandler, MessageHandler
from telegram import Update

from src.command_handlers import main_handler, button

load_dotenv()
TOKEN = os.environ.get("TELEGRAM_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, filename="log")


def init_app() -> Application:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", main_handler))
    app.add_handler(MessageHandler(None, main_handler))
    app.add_handler(CallbackQueryHandler(button))
    # app.add_handler(CommandHandler("record", handle_reset))
    # app.add_error_handler(handle_error)
    return app


if __name__ == '__main__':
    application = init_app()
    logging.info("Starting application")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
