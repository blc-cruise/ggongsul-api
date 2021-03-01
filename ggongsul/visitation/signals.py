import threading

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from slack_sdk import WebhookClient

from .models import Visitation
from ..common.utils import send_slack_msg

slack = WebhookClient(url=settings.SLACK_VISIT_WEBHOOK_URL)


@receiver(post_save, sender=Visitation)
def send_slack_alert(sender, instance: Visitation, created: bool, **kwargs):
    if not created:
        return

    def _async_job():
        send_slack_msg(
            title="꽁술 매장을 방문하였습니다.",
            text=f"## username: {instance.member.username}\n"
            f"## partner: {instance.partner.name}",
            slack_client=slack,
        )

    t = threading.Thread(target=_async_job, args=())
    t.start()
