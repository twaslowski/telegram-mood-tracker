import logging
from dataclasses import dataclass
from functools import partial

from telegram.ext import CallbackContext, JobQueue

from src.model.notification import Notification


@dataclass
class Notifier:
    job_queue: JobQueue

    @staticmethod
    async def reminder(context: CallbackContext, text: str = None):
        """Send the reminder message."""
        if not text:
            text = "Hi! It's time to record your mood :)"
        await context.bot.send_message(context.chat_data.chat_id, text=text)

    def set_notification(self, user_id: int, notification: Notification) -> None:
        """
        Sets a notification for a user.
        :param user_id: The user's Telegram ID.
        :param notification: The notification to set.
        """
        logging.info(f"Setting up notification at {notification.time} for user {user_id}")
        reminder_partial = partial(self.reminder, text=notification.text)
        reminder_partial.__name__ = f"reminder_{user_id}_{notification.time}"
        self.job_queue.run_daily(
            reminder_partial,
            days=(0, 1, 2, 3, 4, 5, 6),
            chat_id=user_id,
            time=notification.time,
        )
