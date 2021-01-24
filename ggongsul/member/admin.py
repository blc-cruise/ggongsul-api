from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from ggongsul.membership.admin import MembershipInline

from .models import Member, MemberDetail, MemberAgreement
from ..visitation.admin import VisitationInline


class MemberDetailInline(admin.StackedInline):
    model = MemberDetail
    can_delete = False


class MemberAgreementInline(admin.StackedInline):
    model = MemberAgreement
    can_delete = False
    readonly_fields = (
        "policy_agreed_at",
        "privacy_agreed_at",
        "adv_agreed_yn",
        "adv_agreed_at",
    )


@admin.register(Member)
class MemberAdmin(UserAdmin):
    inlines = [
        MemberDetailInline,
        MemberAgreementInline,
        MembershipInline,
        VisitationInline,
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
    list_display = (
        "username",
        "is_staff",
        "is_membership_activated",
        "has_membership_benefits",
    )
    search_fields = ("username", "email")
