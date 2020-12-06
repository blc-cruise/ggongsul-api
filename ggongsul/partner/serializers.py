import copy
import logging

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import PartnerDetail, PartnerAgreement


logger = logging.getLogger(__name__)


def only_true_required(value):
    if not value:
        raise serializers.ValidationError("이용약관에 동의하셔야합니다.")


class PartnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerDetail
        exclude = ["secret_token", "created_on", "updated_on", "partner"]


class PartnerAgreementSerializer(serializers.Serializer):
    policy_agree_yn = serializers.BooleanField(
        validators=[only_true_required],
        label=_("제휴점 이용약관에 동의합니다."),
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
