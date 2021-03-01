import threading

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from slack_sdk import WebhookClient

from .models import Membership
from ..common.utils import send_slack_msg

slack = WebhookClient(url=settings.SLACK_MEMBERSHIP_WEBHOOK_URL)


@receiver(pre_save, sender=Membership)
def send_slack_alert(sender, instance: Membership, **kwargs):
    if not instance.is_active:
        return

    if instance.id is not None:
        previous: Membership = Membership.objects.get(id=instance.id)
        if not (previous.is_active is False and instance.is_active is True):
            return

    def _async_job():
        send_slack_msg(
            title="멤버십을 가입하였습니다.",
            text=f"## username: {instance.member.username}",
            slack_client=slack,
        )

    t = threading.Thread(target=_async_job, args=())
    t.start()
