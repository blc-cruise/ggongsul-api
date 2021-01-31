import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.signals import task_failure

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggongsul.settings")

app = Celery("ggongsul")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


@task_failure.connect
def process_failure_signal(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    traceback=None,
    einfo=None,
    **akwargs,
):
    from ggongsul.common.utils import send_slack_msg
    from ggongsul.common.enums import SlackAlertLevel

    if sender.request.retries > 5:
        send_slack_msg(
            title="Celery task unhandled failure",
            text="ERROR: max retry over!!",
            fields={
                "sender": sender,
                "einfo": einfo,
                "exception": exception.__class__.__name__,
                "description": str(exception),
            },
            alert_level=SlackAlertLevel.DANGER,
        )
        return

    if exception.__class__ in [
        # AutoReconnect,
        # ReadTimeout,
        # ConnectTimeout,
    ]:
        backoff = 2 ** sender.request.retries
        send_slack_msg(
            title="Celery task unhandled failure",
            text=f"WARNING: task retry will be execute in {backoff} sec",
            fields={
                "sender": sender,
                "einfo": einfo,
                "exception": exception.__class__.__name__,
                "description": str(exception),
            },
            alert_level=SlackAlertLevel.WARNING,
        )
        sender.retry(countdown=backoff)
        return

    send_slack_msg(
        title="Celery task unhandled failure",
        text=f"ERROR: unhandled exception!",
        fields={
            "sender": sender,
            "einfo": einfo,
            "exception": exception.__class__.__name__,
            "description": str(exception),
        },
        alert_level=SlackAlertLevel.DANGER,
    )
