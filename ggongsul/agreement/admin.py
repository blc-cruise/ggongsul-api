from django.contrib import admin

from ggongsul.agreement.models import Agreement


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    pass
