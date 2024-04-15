import logging
from dataclasses import dataclass
import datetime
from functools import partial

from telegram.ext import CallbackContext, JobQueue

from pyautowire import Injectable, autowire
from tenacity import stop_after_attempt, wait_fixed, retry_if_exception_type, retry

from src.model.notification import Notification
from src.model.record import Record
from src.model.user import User
from src.handlers.record_handlers import create_baseline_record
from src.repository.record_repository import RecordRepository


@dataclass
class Notifier(Injectable):
    job_queue: JobQueue

    async def reminder(self, context: CallbackContext, user_id: int, text: str = None):
        """Send the reminder message."""
        if not text:
            text = "Hi! It's time to record your mood :)"
        await self.send_from_context(context, user_id, text)

    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(TimeoutError),
    )
    async def send_from_context(context: CallbackContext, user_id: int, text: str):
        """Send a message to a user from a context."""
        await context.bot.send_message(user_id, text=text)

    @staticmethod
    @autowire("record_repository")
    async def auto_baseline(
        context: CallbackContext, user: User, record_repository: RecordRepository
    ):
        """Create baseline record for user at scheduled time."""
        latest_user_record = record_repository.get_latest_record_for_user(user.user_id)
        if (
            latest_user_record is None
            or not latest_user_record.timestamp.day == datetime.datetime.now().day
        ):
            await create_baseline_record(user)
            await context.bot.send_message(
                user.user_id, text="A baseline record has been created for you."
            )
        else:
            logging.info(
                f"Record already exists for user {user.user_id} today. Not creating a new one."
            )

    @staticmethod
    def is_from_today(record: Record) -> bool:
        return record.timestamp.date() == datetime.datetime.now().date()

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
                logging.info(f"Removed job {job_name} from job queue")
                break
