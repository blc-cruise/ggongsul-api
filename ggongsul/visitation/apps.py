from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VisitationConfig(AppConfig):
    name = "ggongsul.visitation"
    verbose_name = _("방문 정보")

    def ready(self):
        import ggongsul.visitation.signals
