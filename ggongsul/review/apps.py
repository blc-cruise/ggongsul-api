from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReviewConfig(AppConfig):
    name = "ggongsul.review"
    verbose_name = _("리뷰 정보")
