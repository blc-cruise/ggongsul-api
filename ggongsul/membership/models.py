from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ggongsul.lib.iamport import IMPHelper
from ggongsul.member.models import Member


class Membership(models.Model):
    MEMBERSHIP_PRICE = 4900

    member = models.OneToOneField(
        Member,
        related_name="membership",
        on_delete=models.CASCADE,
        verbose_name=_("멤버십 정보"),
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("멤버십 활성화 여부"),
        help_text=_(
            "멤버십이 활성화 되어있지 않더라도 구독 혜택이 남아 있을 수 있습니다. "
            "멤버십 활성화 여부는 다음달 구독 연장 여부를 결정합니다."
        ),
    )

    last_activated_at = models.DateTimeField(null=True, verbose_name=_("최근 활성화 날짜"))
    last_deactivated_at = models.DateTimeField(null=True, verbose_name=_("최근 비활성화 날짜"))
    last_renewed_at = models.DateTimeField(null=True, verbose_name=_("최근 구독 갱신 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.member.username} 의 멤버십"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("멤버십 정보")
        verbose_name_plural = _("멤버십 정보")

    @transaction.atomic
    def process_subscribe(self):
        cur_datetime = timezone.now()
        # 이미 결제가 되어 있는 경우
        if self.member.has_membership_benefits():
            self.is_active = True
            self.last_activated_at = cur_datetime
            self.save()
            return

        sub = Subscription.create_subscription(
            member=self.member, started_at=cur_datetime
        )
        # 첫 번째 구독일 경우
        if self.last_activated_at is None:
            pass
        # 그 외 경우는 결제
        else:
            Payment.create_payment(
                subscription=sub,
                name="{} 결제".format(str(sub)),
                amount=Membership.MEMBERSHIP_PRICE,
                billing_key=self.member.billing_key,
            )

        self.is_active = True
        self.last_activated_at = cur_datetime
        self.save()

    @transaction.atomic
    def renew_subscription(self):
        cur_datetime = timezone.now()

        old_subscription = self.member.subscriptions.latest("-ended_at")
        new_subscription = Subscription.create_subscription(
            member=self.member, started_at=cur_datetime
        )

        # 이전 구독에서 혜택을 받았다면 결제를 진행한다.
        if old_subscription.has_visitation_records():
            Payment.create_payment(
                subscription=new_subscription,
                name="{} 결제".format(str(new_subscription)),
                amount=Membership.MEMBERSHIP_PRICE,
                billing_key=self.member.billing_key,
            )

        self.last_renewed_at = cur_datetime
        self.save()

    def process_unsubscribe(self):
        cur_datetime = timezone.now()

        # latest_subscription = self.member.subscriptions.latest("ended_at")
        # 환불 정책
        # if (
        #     not latest_subscription.has_visitation_records()
        #     and latest_subscription.is_in_refund_validity_days()
        #     and hasattr(latest_subscription, "payment")
        # ):
        #     latest_subscription.payment.cancel_payment("멤버십 구독 취소 환불 정책에 따른 환불")

        self.is_active = False
        self.last_deactivated_at = cur_datetime
        self.save()


class Subscription(models.Model):
    DEFAULT_VALIDITY_DAYS = 31
    REFUND_VALIDITY_DAYS = 7

    member = models.ForeignKey(
        Member,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name=_("사용자"),
    )
    started_at = models.DateTimeField(verbose_name=_("구독 혜택 시작 날짜"))
    ended_at = models.DateTimeField(verbose_name=_("구독 혜택 종료 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.member.username} 의 {self.started_at.month} 월 구독"

    class Meta:
        ordering = ["-ended_at"]
        verbose_name = _("구독 정보")
        verbose_name_plural = _("구독 정보")

    def payment_yn(self):
        return hasattr(self, "payment")

    payment_yn.short_description = _("결제 여부")
    payment_yn.boolean = True

    def validity_days(self) -> int:
        return (self.ended_at - self.started_at).days

    validity_days.short_description = _("구독 유효 기간(일수)")

    @classmethod
    def create_subscription(
        cls,
        member: Member,
        started_at: datetime,
        validity_days: int = None,
        ended_at: datetime = None,
    ):
        if not validity_days:
            validity_days = cls.DEFAULT_VALIDITY_DAYS
        if not ended_at:
            ended_at = (started_at + timedelta(days=validity_days)).replace(
                hour=23, minute=59, second=59, microsecond=0
            )

        return cls.objects.create(
            member=member,
            started_at=started_at,
            ended_at=ended_at,
        )

    def is_in_refund_validity_days(self) -> bool:
        cur_datetime = timezone.now()
        refund_validity_datetime = self.started_at + timedelta(
            days=Subscription.REFUND_VALIDITY_DAYS
        )
        return cur_datetime <= refund_validity_datetime

    def has_visitation_records(self) -> bool:
        return self.member.visitations.filter(
            created_on__gte=self.started_at, created_on__lt=self.ended_at
        ).exists()


class Payment(models.Model):
    class PaymentType(models.IntegerChoices):
        KAKAOPAY = 1, _("카카오페이")

    subscription = models.OneToOneField(
        Subscription,
        related_name="payment",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("구독 정보"),
    )
    payment_uid = models.CharField(
        unique=True, max_length=64, verbose_name=_("결제 고유 id")
    )
    payment_type = models.IntegerField(
        choices=PaymentType.choices, verbose_name=_("결제 수단")
    )
    imp_uid = models.CharField(max_length=64, verbose_name=_("아임포트 고유 id"))
    amount = models.IntegerField(verbose_name=_("결제 금액"))
    canceled_amount = models.IntegerField(default=0, verbose_name=_("결제 취소 금액"))

    paid_at = models.DateTimeField(verbose_name=_("결제 날짜"))
    canceled_at = models.DateTimeField(null=True, verbose_name=_("결제 취소 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{str(self.subscription)} 의 결제 정보"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("결제 정보")
        verbose_name_plural = _("결제 정보")

    @classmethod
    def create_payment(
        cls, subscription: Subscription, name: str, amount: int, billing_key: str
    ):
        cur_datetime = timezone.now()
        imp_client = IMPHelper()
        payment_uid = (
            f"ggongsul-{cur_datetime.strftime('%y%m%d%H%M%S')}-{secrets.token_hex(3)}"
        )

        resp = imp_client.make_payment(billing_key, payment_uid, amount, name)
        imp_uid = resp["imp_uid"]

        return cls.objects.create(
            subscription=subscription,
            payment_uid=payment_uid,
            payment_type=cls.PaymentType.KAKAOPAY,
            imp_uid=imp_uid,
            amount=amount,
            paid_at=cur_datetime,
        )

    def cancel_payment(self, reason: str = None):
        cur_datetime = timezone.now()
        imp_client = IMPHelper()

        resp = imp_client.cancel_payment(self.imp_uid, self.payment_uid, reason=reason)
        self.canceled_at = cur_datetime
        self.canceled_amount = resp["cancel_amount"]
        self.save()
