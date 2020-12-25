from typing import Tuple

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken

from ggongsul.core import exceptions
from ggongsul.lib.kakao import KakaoLoginHelper


class Member(AbstractUser):
    first_name = None
    last_name = None

    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("사용자")
        verbose_name_plural = _("사용자")

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        raise NotImplementedError()

    def get_common_attr(self):
        return {"username": self.username, "email": self.email}

    def create_refresh_token(self):
        token: RefreshToken = RefreshToken.for_user(self)

        for k, v in self.get_common_attr().items():
            token[k] = v

        return token

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=["last_login"])

    def process_login(self):
        self.update_last_login()
        token = self.create_refresh_token()

        return {"refresh": str(token), "access": str(token.access_token)}


class MemberDetail(models.Model):
    class ChannelIn(models.IntegerChoices):
        FRIEND = 1, _("지인 추천")
        ADV = 2, _("페북,인스타 광고")
        BLOG = 3, _("블로그")
        COMMUNITY = 4, _("각종 커뮤니티")
        ETC = 5, _("기타")

    member = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="detail", verbose_name=_("멤버")
    )
    channel_in = models.IntegerField(
        choices=ChannelIn.choices, default=ChannelIn.ETC, verbose_name=_("유입 채널")
    )

    def __str__(self):
        return self.member.username + " 상세 정보"

    def __repr__(self):
        return self.__str__()


class MemberAgreement(models.Model):
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name="agreement",
        verbose_name=_("동의서"),
    )
    policy_agreed_at = models.DateTimeField(null=True, verbose_name=_("이용약관 동의 날짜"))
    privacy_agreed_at = models.DateTimeField(null=True, verbose_name=_("개인정보 이용 동의 날짜"))
    adv_agreed_yn = models.BooleanField(default=False, verbose_name=_("광고 수신 동의 여부"))
    adv_agreed_at = models.DateTimeField(null=True, verbose_name=_("광고 수신 동의 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("이용약관 동의서")
        verbose_name_plural = _("이용약관 동의서")

    def __str__(self):
        return self.member.username + " 이용약관 동의서"

    def __repr__(self):
        return self.__str__()


class SocialAccount(models.Model):
    class Provider(models.TextChoices):
        KAKAO = "kakao", _("카카오")

    member = models.ForeignKey(
        Member,
        related_name="social_accounts",
        on_delete=models.CASCADE,
        verbose_name=_("사용자"),
    )

    provider = models.CharField(
        max_length=20, choices=Provider.choices, verbose_name=_("소셜 인증 제공 업체")
    )
    uid = models.CharField(max_length=120, verbose_name=_("소셜 인증 Id"))
    unlink_yn = models.BooleanField(default=False, verbose_name=_("소셜 계정 연결 여부"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __str__(self):
        return self.member.username + " 소셜 계정 정보"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def is_valid_social_account(
        provider: Provider, access_token: str, uid: str
    ) -> Tuple[bool, str]:
        if provider == SocialAccount.Provider.KAKAO:
            try:
                user_info = KakaoLoginHelper(access_token=access_token).get_user_info()
            except exceptions.ERROR:
                return False, _("kakao access token 이 정상적이지 않습니다.")

            _uid = user_info.get("id", None)
            if not _uid or uid != str(_uid):
                return False, _(f"uid {uid} 는 유효하지 않습니다.")

            return True, ""

    class Meta:
        unique_together = ("provider", "uid")
        ordering = ("-id",)
        verbose_name = _("소셜 계정")
        verbose_name_plural = _("소셜 계정")
