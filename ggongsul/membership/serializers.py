import logging

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from ggongsul.core.generics import APISerializer
from ggongsul.membership.models import MemberShip

logger = logging.getLogger(__name__)


class SubscribeSerializer(APISerializer):
    def validate(self, attrs: dict):
        member = self.context["request"].user
        if member.is_membership_activated:
            raise ValidationError(_("이미 멤버십을 구독중입니다."))

        if not member.is_billing_key_exist:
            raise ValidationError(_("빌링키가 등록 되어있지 않습니다."))

        membership, created = MemberShip.objects.get_or_create(member=member)
        membership.process_subscribe()
        return {"message": "okay"}


class UnsubscribeSerializer(APISerializer):
    def validate(self, attrs: dict):
        member = self.context["request"].user
        if not member.is_membership_activated:
            raise ValidationError(_("구독 중인 멤버십이 없습니다."))

        member.membership.process_unsubscribe()
        return {"message": "okay"}
