from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from django.utils.translation import gettext_lazy as _

from ggongsul.member.models import Member


class MembershipAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user: Member = super().get_user(validated_token)
        if not user.has_membership:
            raise AuthenticationFailed(
                _("멤버십에 가입한 멤버가 아닙니다."), code="has_not_membership"
            )
        return user
