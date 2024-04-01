import logging

from telegram import Update

from src.config import configuration
from kink import di
from src.handlers.util import send
from src.reminder import Notifier
from src.repository import user_repository


async def create_user(update: Update, _) -> None:
    """
    Handles /start command.
    Creates user based on the user_id included in the update object.
    :param update: Update from the Telegram bot.
    :param _: CallbackContext: is irrelevant
    :return:
    """
    # Declare introduction text.
    bullet_point_list = "\n".join(
        [f"- {metric.name.capitalize()}" for metric in configuration.get_metrics()]
    )
    introduction_text = (
        "Hi! You can track your mood with me. "
        "Simply type /record to get started. By default, "
        f"I will track the following metrics:\n {bullet_point_list}"
    )

    # Handle registration
    user_id = update.effective_user.id
    if not user_repository.find_user(user_id):
        logging.info(f"Creating user {user_id}")
        # todo all of this could use some decoupling
        user_repository.create_user(user_id)
        for notification in configuration.get_notifications():
            di[Notifier].set_notification(user_id, notification)
        await send(update, text=introduction_text)
    # User already exists
    else:
        logging.info(f"Received /start, but user {user_id} already exists")
        await send(
            update,
            text="You are already registered! If you want to re-assess your metrics or notifications, "
                 "type /metrics or /notifications to do so.",
        )
