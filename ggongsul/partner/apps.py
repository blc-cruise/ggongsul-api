from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PartnerConfig(AppConfig):
    name = "ggongsul.partner"
    verbose_name = _("업체 정보")

    def ready(self):
        import ggongsul.partner.signals
