import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from ggongsul.core import exceptions
from ggongsul.lib.kakao import KakaoLoginHelper
from ggongsul.member.models import SocialAccount

logger = logging.getLogger(__name__)


class LoginSerializer(serializers.Serializer):
    login_type = serializers.ChoiceField(choices=SocialAccount.Provider.choices)
    uid = serializers.CharField()
    access_token = serializers.CharField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()

    def validate(self, attrs: dict):
        uid = attrs["uid"]
        access_token = attrs["access_token"]

        # uid validation
        try:
            user_info = KakaoLoginHelper(access_token=access_token).get_user_info()
        except exceptions.ERROR:
            raise ValidationError(f"invalide kakao id {uid}")

        _uid = user_info.get("id", None)
        if not _uid or uid != str(_uid):
            raise ValidationError(f"invalide kakao id {uid}")

        try:
            sa = SocialAccount.objects.get(
                provider=SocialAccount.Provider.KAKAO, uid=uid
            )
        except SocialAccount.DoesNotExist:
            raise AuthenticationFailed(f"there is no member for uid {uid}")

        sa.member.update_last_login()
        token = sa.member.create_refresh_token()

        return {"refresh": str(token), "access": str(token.access_token)}
