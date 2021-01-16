from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MembershipConfig(AppConfig):
    name = "ggongsul.membership"
    verbose_name = _("멤버십 정보")
