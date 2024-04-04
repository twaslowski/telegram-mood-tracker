import logging

from pyautowire import autowire, Injectable
from src.exception.auto_baseline_exception import (
    MetricBaselinesNotDefinedException,
    AutoBaselineTimeNotDefinedException,
)
from src.model.user import User
from src.notifier import Notifier
from src.repository.user_repository import UserRepository


class UserService(Injectable):
    """
    Service for managing user-related operations.
    Most of this functionality was moved here from the user_handlers.py file for better separation of concerns.
    """

    user_repository: UserRepository
    notifier: Notifier

    # todo this works, but can use some improvements
    @autowire("user_repository", "notifier")
    def __init__(self, user_repository: UserRepository, notifier: Notifier):
        self.user_repository = user_repository
        self.notifier = notifier

    def toggle_auto_baseline(self, user: User) -> bool:
        """
        Toggles the auto-baseline feature for a user.
        :param user: User to toggle the auto-baseline feature for.
        :return: True if auto-baseline is enabled, False otherwise.
        """
        if user.has_auto_baseline_enabled():
            logging.info(f"Disabling auto-baseline for user {user.user_id}")
            user.disable_auto_baseline()
            self.notifier.remove_auto_baseline(user)
            self.user_repository.update_user(user)
            return False
        else:
            return self.enable_auto_baseline(user)

    def enable_auto_baseline(self, user: User) -> bool:
        """
        Enables the auto-baseline feature for a user.
        :param user: User to enable the auto-baseline feature for.
        :return: True if auto-baseline is enabled.
        :raises AutoBaselineException: if the user does not have baselines defined or the auto-baseline time is not set.
        """
        logging.info(f"Enabling auto-baseline for user {user.user_id}")
        if not user.has_baselines_defined():
            logging.error(
                f"Baselines not defined for all metrics for user {user.user_id}"
            )
            raise MetricBaselinesNotDefinedException(user)
        if not user.get_auto_baseline_time():
            logging.error(f"Auto-baseline time not defined for user {user.user_id}")
            raise AutoBaselineTimeNotDefinedException()
        user.enable_auto_baseline()
        self.notifier.create_auto_baseline(user)
        self.user_repository.update_user(user)
        return True

    def schedule_auto_baselines(self):
        """
        Sets up the auto-baseline for all users in the database.
        """
        for user in self.user_repository.find_all_users():
            if user.has_auto_baseline_enabled() and user.has_baselines_defined():
                self.notifier.create_auto_baseline(user)

    def schedule_notifications(self) -> None:
        """
        Adds reminders to the job queue for all users that have configured reminders.
        """
        for user in self.user_repository.find_all_users():
            self.setup_notifications(user)

    def find_user(self, user_id: int) -> User | None:
        return self.user_repository.find_user(user_id)

    def create_user(self, user_id: int) -> User:
        logging.info(f"Creating user {user_id}")
        user = self.user_repository.create_user(user_id)
        self.setup_notifications(user)
        self.setup_auto_baseline(user)
        return user

    def setup_notifications(self, user: User) -> None:
        logging.info(f"Setting up notifications for user {user.user_id}")
        for notification in user.get_notifications():
            self.notifier.create_notification(user.user_id, notification)

    def setup_auto_baseline(self, user: User) -> None:
        if user.has_auto_baseline_enabled():
            self.enable_auto_baseline(user)
