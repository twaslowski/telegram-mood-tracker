import logging

from telegram import Update

from src.autowiring.inject import autowire
from src.handlers.util import send
from src.model.user import User
from src.service.user_service import UserService


@autowire("user_service")
async def create_user(update: Update, _, user_service: UserService) -> User:
    """
    Handles /start command.
    Creates user based on the user_id included in the update object.
    :param user_service: autowired.
    :param update: Update from the Telegram bot.
    :param _: CallbackContext: is irrelevant
    :return:
    """
    # Handle registration
    user_id = update.effective_user.id
    if not user_service.find_user(user_id):
        user = user_service.create_user(user_id)
        await send(update, text=introduction_text(user))
        return user
    # User already exists
    else:
        logging.info(f"Received /start, but user {user_id} already exists")
        await send(
            update,
            text="You are already registered! If you want to re-assess your metrics or notifications, "
            "type /metrics or /notifications to do so.",
        )


@autowire("user_service")
async def toggle_auto_baseline(update: Update, _, user_service: UserService) -> None:
    user_id = update.effective_user.id
    user = user_service.find_user(user_id)
    # if baseline is not already enabled and the user has the necessary configuration
    result = user_service.toggle_auto_baseline(user)
    if result:
        await send(
            update,
            text=f"Auto-baseline enabled; baseline records will "
            f"be created daily at {user.get_auto_baseline_time().isoformat()} UTC.",
        )
    else:
        await send(update, text="Auto-baseline disabled.")


def introduction_text(user: User) -> str:
    bullet_point_list = "\n".join(
        [f"- {metric.name.capitalize()}" for metric in user.metrics]
    )
    return (
        "Hi! You can track your mood with me. "
        "Simply type /record to get started. By default, "
        f"I will track the following metrics:\n {bullet_point_list}"
    )
