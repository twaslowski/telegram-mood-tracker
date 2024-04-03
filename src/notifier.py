import logging
from dataclasses import dataclass
from functools import partial

from telegram.ext import CallbackContext, JobQueue

from src.autowiring.injectable import Injectable
from src.model.notification import Notification
from src.model.user import User
from src.handlers.record_handlers import create_baseline_record


@dataclass
class Notifier(Injectable):
    job_queue: JobQueue

    @staticmethod
    async def reminder(context: CallbackContext, user_id: int, text: str = None):
        """Send the reminder message."""
        if not text:
            text = "Hi! It's time to record your mood :)"
        await context.bot.send_message(user_id, text=text)

    @staticmethod
    async def auto_baseline(context: CallbackContext, user: User):
        """Create baseline record for user at scheduled time."""
        await create_baseline_record(user)
        await context.bot.send_message(
            user.user_id, text="A baseline record has been created for you."
        )

    def create_notification(self, user_id: int, notification: Notification) -> str:
        """
        Sets a notification for a user.
        :param user_id: The user's Telegram ID.
        :param notification: The notification to set.
        :return: The name of the job.
        """
        logging.info(
            f"Setting up notification at {notification.time} for user {user_id}"
        )
        reminder_partial = partial(
            self.reminder, user_id=user_id, text=notification.text
        )
        reminder_partial.__name__ = f"reminder_{user_id}_{notification.time}"
        job = self.job_queue.run_daily(
            reminder_partial,
            days=(0, 1, 2, 3, 4, 5, 6),
            chat_id=user_id,
            time=notification.time,
        )
        return job.name

    def create_auto_baseline(self, user: User):
        """
        Create baseline record for user at scheduled time.
        :param user: The user to create a baseline for.
        """
        logging.info(f"Creating auto-baseline for user {user.user_id}")
        baseline_partial = partial(self.auto_baseline, user=user)
        baseline_partial.__name__ = f"baseline_{user.user_id}"
        self.job_queue.run_daily(
            baseline_partial,
            days=(0, 1, 2, 3, 4, 5, 6),
            chat_id=user.user_id,
            time=user.get_auto_baseline_time(),
        )

    def remove_auto_baseline(self, user: User):
        """
        Remove the auto-baseline job for the user.
        :param user: The user to remove the auto-baseline for.
        """
        logging.info(f"Removing auto-baseline for user {user.user_id}")
        baseline_job_name = f"baseline_{user.user_id}"
        self.remove_job(baseline_job_name)

    def find_job(self, name: str):
        """
        Find a job by name.
        :param name: The name of the job to find
        :return: The job if found, None otherwise.
        """
        for job in self.job_queue.jobs():
            if job.name == name:
                return job
        return None

    def remove_job(self, job_name: str):
        """
        Remove a job by name.
        :param job_name: The name of the job to remove.
        """
        for job in self.job_queue.jobs():
            if job.name == job_name:
                job.schedule_removal()
                break
