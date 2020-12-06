from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MemberConfig(AppConfig):
    name = "ggongsul.member"
    verbose_name = _("사용자 정보")
