import logging
import os

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from src.config.config import ConfigurationProvider
from src.handlers.error_handler import error_handler
from src.repository.initialize import initialize_database
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
    format=" %(levelname)s - %(asctime)s - %(name)s - %(message)s", level=logging.INFO
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
