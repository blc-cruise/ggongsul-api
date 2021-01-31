"""
WSGI config for ggongsul project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ggongsul.settings")

application = get_wsgi_application()

from django.utils.translation import gettext_lazy as _
from django_celery_beat import apps

apps.BeatConfig.verbose_name = _("정기 배치 작업")
