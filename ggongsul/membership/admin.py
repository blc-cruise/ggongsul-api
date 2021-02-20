from django.contrib import admin

from ggongsul.membership.models import Membership, Subscription, Payment


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 1
    readonly_fields = (
        "last_activated_at",
        "last_deactivated_at",
        "last_renewed_at",
        "created_on",
        "updated_on",
    )
    can_delete = False


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ("paid_at", "canceled_at")
    can_delete = False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    inlines = (PaymentInline,)
    list_display = ("__str__", "payment_yn", "validity_days")
