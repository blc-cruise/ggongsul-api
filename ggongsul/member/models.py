from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class Member(AbstractUser):
    class Meta:
        verbose_name = _("사용자")
        verbose_name_plural = _("사용자")
