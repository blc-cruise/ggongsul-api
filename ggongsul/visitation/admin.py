from django.contrib import admin

from ggongsul.visitation.models import Visitation


class VisitationInline(admin.TabularInline):
    model = Visitation
    extra = 0
    readonly_fields = ("partner", "created_on", "updated_on")
    can_delete = False
