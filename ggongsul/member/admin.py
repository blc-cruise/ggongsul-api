from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from rangefilter.filter import DateTimeRangeFilter

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
        "date_joined",
        "channel_in",
        "recommended_place",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        ("date_joined", DateTimeRangeFilter),
    )
    search_fields = ("username", "email")

    def channel_in(self, obj: Member):
        v = obj.detail.channel_in
        for idx, help_txt in obj.detail.ChannelIn.choices:
            if v == idx:
                return help_txt
        return None

    def recommended_place(self, obj: Member):
        return obj.detail.recommended_place

    channel_in.short_description = _("유입 채널")
    recommended_place.short_description = _("추천 장소")
