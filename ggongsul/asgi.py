"""
ASGI config for ggongsul project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggongsul.settings")

application = get_asgi_application()

from django.utils.translation import gettext_lazy as _
from django_celery_beat import apps

apps.BeatConfig.verbose_name = _("정기 배치 작업")
