from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AgreementConfig(AppConfig):
    name = "ggongsul.agreement"
    verbose_name = _("이용 약관")
