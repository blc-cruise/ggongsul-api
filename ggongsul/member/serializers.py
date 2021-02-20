import logging
import secrets

from typing import Optional

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.validators import UniqueValidator

from ggongsul.core.generics import APISerializer
from ggongsul.member.models import (
    SocialAccount,
    MemberDetail,
    Member,
    MemberProfileImage,
)

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

        if not sa.member.is_active:
            raise AuthenticationFailed(_("탈퇴한 멤버입니다."))

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
    profile_image = serializers.PrimaryKeyRelatedField(
        queryset=MemberProfileImage.objects.all(), allow_null=True
    )

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

        profile_image: Optional[MemberProfileImage] = attrs.get("profile_image", None)
        if profile_image and profile_image.member_id:
            raise ValidationError(_("이미 다른 멤버가 사용중인 프로필 사진입니다."))

        if SocialAccount.objects.filter(provider=signup_type, uid=uid).exists():

            # 해당 소셜 계정이 active하면
            if (
                SocialAccount.objects.filter(provider=signup_type, uid=uid)
                .last()
                .member.is_active
            ):
                raise ValidationError(_("해당 소셜 계정으로 가입한 멤버가 존재합니다."))

            # 해당 소셜 계정이 deactive하면 기존 정보를 update시킨다.
            m = self._update_social_account_member(
                username=attrs["username"],
                channel_in=attrs["channel_in"],
                uid=uid,
                provider=signup_type,
                adv_agree_yn=attrs["adv_agree_yn"],
            )

            return m.process_login()

        m = self._create_social_account_member(
            username=attrs["username"],
            channel_in=attrs["channel_in"],
            uid=uid,
            provider=signup_type,
            adv_agree_yn=attrs["adv_agree_yn"],
            profile_image=profile_image,
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
        profile_image: Optional[MemberProfileImage] = None,
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

        if profile_image:
            profile_image.member_id = m.id
            profile_image.save()

        # save related objects
        m.detail.save()
        m.agreement.save()
        m.save()
        return m

    @transaction.atomic
    def _update_social_account_member(
        self,
        username: str,
        channel_in: MemberDetail.ChannelIn,
        provider: SocialAccount.Provider,
        uid: str,
        adv_agree_yn: bool,
        profile_image: Optional[MemberProfileImage] = None,
    ):
        m = SocialAccount.objects.filter(provider=provider, uid=uid).last().member
        cur_datetime = timezone.now()

        # username 변경
        m.username = username
        m.is_active = True
        # add member detail
        m.detail.channel_in = channel_in

        # add member agreement
        m.agreement.policy_agreed_at = cur_datetime
        m.agreement.privacy_agreed_at = cur_datetime
        if adv_agree_yn:
            m.agreement.adv_agreed_yn = adv_agree_yn
            m.agreement.adv_agreed_at = cur_datetime

        if profile_image:
            # 이미 profile image 가 존재하는 경우
            if hasattr(m, "profile_image"):
                m.profile_image.member_id = None
                m.profile_image.save()

            profile_image.member_id = m.id
            profile_image.save()

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
    next_membership_payment = serializers.SerializerMethodField()
    start_subscription_date = serializers.SerializerMethodField()
    end_subscription_date = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    def get_next_membership_payment(self, obj: Member):
        np = obj.next_membership_payment()
        if not np:
            return None
        return np.strftime("%Y년 %m월 %d일")

    def get_start_subscription_date(self, obj: Member):
        sub = obj.active_subscription()
        if not sub:
            return None
        return sub.started_at.strftime("%Y년 %m월 %d일")

    def get_end_subscription_date(self, obj: Member):
        sub = obj.active_subscription()
        if not sub:
            return None
        return sub.ended_at.strftime("%Y년 %m월 %d일")

    def get_profile_image(self, obj: Member):
        if hasattr(obj, "profile_image"):
            return obj.profile_image.image.url
        return settings.DEFAULT_PROFILE_IMAGE_URL

    class Meta:
        model = Member
        fields = [
            "id",
            "username",
            "profile_image",
            "has_membership_benefits",
            "is_membership_activated",
            "total_membership_days",
            "total_visitation_cnt",
            "next_membership_payment",
            "start_subscription_date",
            "end_subscription_date",
        ]


class MemberProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfileImage
        fields = [
            "id",
            "image",
        ]


class UpdateProfileImageSerializer(APISerializer):
    profile_image = serializers.PrimaryKeyRelatedField(
        queryset=MemberProfileImage.objects.all()
    )

    def validate(self, attrs: dict):
        profile_image: MemberProfileImage = attrs["profile_image"]
        if profile_image.member_id:
            raise ValidationError(_("이미 다른 멤버가 사용중인 프로필 사진입니다."))

        member: Member = self.context["request"].user
        if hasattr(member, "profile_image"):
            member.profile_image.member_id = None
            member.profile_image.save()

        profile_image.member_id = member.id
        profile_image.save()

        return {"profile_image": profile_image.image.url}
