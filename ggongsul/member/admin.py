from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from ggongsul.membership.admin import MembershipInline

from .models import Member, MemberDetail, MemberAgreement


class MemberDetailInline(admin.StackedInline):
    model = MemberDetail


class MemberAgreementInline(admin.StackedInline):
    model = MemberAgreement


@admin.register(Member)
class MemberAdmin(UserAdmin):
    inlines = [
        MemberDetailInline,
        MemberAgreementInline,
        MembershipInline,
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("email",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "is_staff")
    search_fields = ("username", "email")
