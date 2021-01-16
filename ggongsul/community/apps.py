from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommunityConfig(AppConfig):
    name = "ggongsul.community"
    verbose_name = _("커뮤니티 정보")
