import datetime

from src.model.notification import Notification


def test_add_to_job_queue(notifier):
    job = notifier.create_notification(
        123456,
        Notification(time=datetime.datetime.now().time(), text="Test notification."),
    )
    assert notifier.find_job(job) is not None
    notifier.remove_job(job)
    assert job not in notifier.job_queue.jobs()
