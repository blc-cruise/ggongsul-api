import logging
import secrets

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.validators import UniqueValidator

from ggongsul.core.generics import APISerializer
from ggongsul.member.models import SocialAccount, MemberDetail, Member

logger = logging.getLogger(__name__)


class LoginSerializer(APISerializer):
    login_type = serializers.ChoiceField(choices=SocialAccount.Provider.choices)
    uid = serializers.CharField()
    access_token = serializers.CharField()

    def validate(self, attrs: dict):
        login_type = attrs["login_type"]
        uid = attrs["uid"]
        access_token = attrs["access_token"]

        is_valid, msg = SocialAccount.is_valid_social_account(
            login_type, access_token, uid
        )
        if not is_valid:
            raise ValidationError(msg)

        try:
            sa = SocialAccount.objects.get(provider=login_type, uid=uid)
        except SocialAccount.DoesNotExist:
            raise AuthenticationFailed(_("해당 uid로 가입된 멤버가 없습니다."))

        return sa.member.process_login()


class SignupSerializer(APISerializer):
    signup_type = serializers.ChoiceField(choices=SocialAccount.Provider.choices)
    uid = serializers.CharField()
    access_token = serializers.CharField()

    policy_agree_yn = serializers.BooleanField()
    privacy_agree_yn = serializers.BooleanField()
    adv_agree_yn = serializers.BooleanField()

    username = serializers.CharField(
        max_length=150, validators=[UniqueValidator(queryset=Member.objects.all())]
    )
    channel_in = serializers.ChoiceField(choices=MemberDetail.ChannelIn.choices)

    def validate_policy_agree_yn(self, value: bool):
        if not value:
            raise ValidationError(_("이용약관에 반드시 동의 해야합니다."))
        return value

    def validate_privacy_agree_yn(self, value: bool):
        if not value:
            raise ValidationError(_("개인정보 이용 동의에 반드시 동의 해야합니다."))
        return value

    def validate(self, attrs: dict):
        signup_type = attrs["signup_type"]
        uid = attrs["uid"]
        access_token = attrs["access_token"]

        is_valid, msg = SocialAccount.is_valid_social_account(
            signup_type, access_token, uid
        )
        if not is_valid:
            raise ValidationError(msg)

        if SocialAccount.objects.filter(provider=signup_type, uid=uid).exists():
            raise ValidationError(_("해당 소셜 계정으로 가입한 멤버가 존재합니다."))

        m = self._create_social_account_member(
            username=attrs["username"],
            channel_in=attrs["channel_in"],
            uid=uid,
            provider=signup_type,
            adv_agree_yn=attrs["adv_agree_yn"],
        )
        return m.process_login()

    @transaction.atomic
    def _create_social_account_member(
        self,
        username: str,
        channel_in: MemberDetail.ChannelIn,
        provider: SocialAccount.Provider,
        uid: str,
        adv_agree_yn: bool,
    ):
        # create member
        m: Member = Member.objects.create_user(
            username=username, email=None, password=secrets.token_urlsafe(16)
        )
        SocialAccount.objects.create(member=m, provider=provider, uid=uid)
        cur_datetime = timezone.now()

        # add member detail
        m.detail.channel_in = channel_in

        # add member agreement
        m.agreement.policy_agreed_at = cur_datetime
        m.agreement.privacy_agreed_at = cur_datetime
        if adv_agree_yn:
            m.agreement.adv_agreed_yn = adv_agree_yn
            m.agreement.adv_agreed_at = cur_datetime

        # save related objects
        m.detail.save()
        m.agreement.save()
        m.save()
        return m


class CheckUsernameSerializer(APISerializer):
    username = serializers.CharField(
        max_length=150, validators=[UniqueValidator(queryset=Member.objects.all())]
    )


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "username",
        ]
