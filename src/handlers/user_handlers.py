import logging

from telegram import Update

from src.autowiring.inject import autowire
from src.config.auto_baseline import AutoBaselineConfig
from src.config.config import Configuration
from src.handlers.util import send
from src.notifier import Notifier
from src.repository.user_repository import UserRepository


@autowire("user_repository")
async def create_user(update: Update, _, user_repository: UserRepository) -> None:
    """
    Handles /start command.
    Creates user based on the user_id included in the update object.
    :param user_repository: autowired.
    :param update: Update from the Telegram bot.
    :param _: CallbackContext: is irrelevant
    :return:
    """
    # Handle registration
    user_id = update.effective_user.id
    if not user_repository.find_user(user_id):
        logging.info(f"Creating user {user_id}")
        user_repository.create_user(user_id)
        setup_notifications(user_id)
        await send(update, text=introduction_text())
    # User already exists
    else:
        logging.info(f"Received /start, but user {user_id} already exists")
        await send(
            update,
            text="You are already registered! If you want to re-assess your metrics or notifications, "
            "type /metrics or /notifications to do so.",
        )


@autowire("notifier", "user_repository")
async def toggle_auto_baseline(
    update: Update, _, notifier: Notifier, user_repository: UserRepository
) -> None:
    user_id = update.effective_user.id
    user = user_repository.find_user(user_id)
    if not user.has_auto_baseline_enabled():
        if user.has_baselines_defined():
            notifier.create_auto_baseline(user)
            user.auto_baseline_config = AutoBaselineConfig.default()
            user_repository.update_user(user)
            await send(
                update,
                text=f"Auto-baseline enabled; baseline records will "
                f"be created daily at {user.get_auto_baseline_time().isoformat()} UTC.",
            )
        else:
            logging.warning(
                f"User {user_id} attempted enabling auto-baseline, "
                f"but does not have all baselines configured."
            )
            await send(
                update,
                text=f"You need to configure all baselines first. "
                f"Metrics without baselines: {','.join(user.get_metrics_without_baselines())}",
            )
    else:
        user.auto_baseline_config.enabled = False
        user_repository.update_user(user)
        notifier.remove_auto_baseline(user)
        await send(update, text="Auto-baseline disabled.")


@autowire("configuration", "notifier")
def setup_notifications(
    user_id: int, configuration: Configuration, notifier: Notifier
) -> None:
    for notification in configuration.get_notifications():
        notifier.create_notification(user_id, notification)


@autowire("configuration")
def introduction_text(configuration: Configuration) -> str:
    bullet_point_list = "\n".join(
        [f"- {metric.name.capitalize()}" for metric in configuration.get_metrics()]
    )
    return (
        "Hi! You can track your mood with me. "
        "Simply type /record to get started. By default, "
        f"I will track the following metrics:\n {bullet_point_list}"
    )
