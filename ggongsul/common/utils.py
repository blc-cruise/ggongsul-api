import sys
import traceback
import logging
import typing

from django.conf import settings
from slack_sdk import WebhookClient

from .enums import SlackAlertLevel
from ..core.decorators import exponential_backoff_retry

logger = logging.getLogger(__name__)
slack_info = WebhookClient(url=settings.SLACK_INFO_WEBHOOK_URL)
slack_error = WebhookClient(url=settings.SLACK_ERROR_WEBHOOK_URL)


def logging_traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    error_message = "".join(lines)
    logger.error(error_message)


@exponential_backoff_retry
def send_slack_msg(
    title: str,
    text: str = None,
    fields: typing.Union[list, dict] = None,
    attachments: typing.List[dict] = None,
    alert_level: typing.Union[str, SlackAlertLevel] = SlackAlertLevel.INFO,
    slack_client: WebhookClient = None,
):
    if isinstance(alert_level, SlackAlertLevel):
        alert_level = alert_level.value

    if slack_client:
        slack = slack_client
    elif alert_level == SlackAlertLevel.INFO.value:
        slack = slack_info
    else:
        slack = slack_error

    if attachments:
        slack.send(
            text=title,
            attachments=attachments,
        )
        return

    attachment = {"title": title, "color": alert_level}

    if text:
        attachment["text"] = text
    if fields:
        if type(fields) is list:
            attachment["fields"] = fields
        elif type(fields) is dict:
            attachment["fields"] = [
                {"title": str(a), "value": str(fields[a]), "short": True}
                for a in fields
            ]

    slack.send(attachments=[attachment])
