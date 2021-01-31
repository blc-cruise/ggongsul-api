from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from ggongsul.common.enums import SlackAlertLevel
from ggongsul.common.utils import send_slack_msg
from ggongsul.member.models import Member
from ggongsul.membership.models import Membership


@shared_task
def check_expire_membership():
    tomorrow = (timezone.now() + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    total_membership_cnt = 0
    renew_cnt = 0

    for member in Member.objects.filter(is_active=True, membership__is_active=True):
        total_membership_cnt += 1
        if member.next_membership_payment() >= tomorrow:
            continue

        renew_subscription.delay(member.id)
        renew_cnt += 1

    send_slack_msg(
        title="Check Expire Membership",
        text=f"successfully done!",
        fields={
            "total membership count": total_membership_cnt,
            "renew subscription count": renew_cnt,
        },
        alert_level=SlackAlertLevel.INFO,
    )


@shared_task
def renew_subscription(member_id: int):
    membership = Membership.objects.get(member_id=member_id)
    membership.renew_subscription()
