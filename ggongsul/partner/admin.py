from django.contrib import admin
from .models import Partner, PartnerDetail, PartnerCategory, PartnerAgreement


class PartnerDetailInline(admin.StackedInline):
    model = PartnerDetail
    exclude = ("secret_token",)


class PartnerAgreementInline(admin.StackedInline):
    model = PartnerAgreement


@admin.register(PartnerCategory)
class PartnerCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines = [PartnerAgreementInline, PartnerDetailInline]
    list_display = ("name", "address", "contact_name", "detail_update_url")
