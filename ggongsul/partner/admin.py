from django.contrib import admin
from .models import Partner, PartnerDetail, PartnerCategory


class PartnerDetailInline(admin.StackedInline):
    model = PartnerDetail
    exclude = ("secret_token",)


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = [PartnerDetailInline]
    list_display = ("name", "address", "contact_name", "detail_update_url")
