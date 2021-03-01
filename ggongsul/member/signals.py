import threading

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from slack_sdk import WebhookClient

from .models import Member, MemberDetail, MemberAgreement
from ..common.utils import send_slack_msg

slack = WebhookClient(url=settings.SLACK_JOIN_WEBHOOK_URL)


@receiver(post_save, sender=Member)
def create_profile(sender, instance: Member, created: bool, **kwargs):
    if created:
        MemberDetail.objects.create(member=instance)
        MemberAgreement.objects.create(member=instance)


@receiver(post_save, sender=Member)
def send_slack_alert(sender, instance: Member, created: bool, **kwargs):
    if not created:
        return

    def _async_job():
        send_slack_msg(
            title="새로운 회원이 가입했습니다.",
            text=f"## username: {instance.username}",
            slack_client=slack,
        )

    t = threading.Thread(target=_async_job, args=())
    t.start()
