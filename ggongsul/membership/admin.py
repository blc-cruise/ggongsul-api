from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ggongsul.membership.models import Membership, Subscription, Payment


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 1


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    inlines = (PaymentInline,)
    list_display = (
        "__str__",
        "payment_yn",
    )
