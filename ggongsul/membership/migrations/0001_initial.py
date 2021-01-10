# Generated by Django 3.1.3 on 2021-01-10 17:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "validity_days",
                    models.IntegerField(default=30, verbose_name="구독 유효 기간(일수)"),
                ),
                ("started_at", models.DateTimeField(verbose_name="구독 혜택 시작 날짜")),
                ("ended_at", models.DateTimeField(verbose_name="구독 혜택 종료 날짜")),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성 날짜"),
                ),
                (
                    "updated_on",
                    models.DateTimeField(auto_now=True, verbose_name="최근 정보 변경 날짜"),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "구독 정보",
                "verbose_name_plural": "구독 정보",
                "ordering": ["-ended_at"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "payment_uid",
                    models.CharField(
                        max_length=64, unique=True, verbose_name="결제 고유 id"
                    ),
                ),
                (
                    "payment_type",
                    models.IntegerField(choices=[(1, "카카오페이")], verbose_name="결제 수단"),
                ),
                ("imp_uid", models.CharField(max_length=64, verbose_name="아임포트 고유 id")),
                ("amount", models.IntegerField(verbose_name="결제 금액")),
                (
                    "canceled_amount",
                    models.IntegerField(default=0, verbose_name="결제 취소 금액"),
                ),
                ("paid_at", models.DateTimeField(verbose_name="결제 날짜")),
                (
                    "canceled_at",
                    models.DateTimeField(null=True, verbose_name="결제 취소 날짜"),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성 날짜"),
                ),
                (
                    "updated_on",
                    models.DateTimeField(auto_now=True, verbose_name="최근 정보 변경 날짜"),
                ),
                (
                    "subscription",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="payment",
                        to="membership.subscription",
                        verbose_name="구독 정보",
                    ),
                ),
            ],
            options={
                "verbose_name": "결제 정보",
                "verbose_name_plural": "결제 정보",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=False,
                        help_text="멤버십이 활성화 되어있지 않더라도 구독 혜택이 남아 있을 수 있습니다. 멤버십 활성화 여부는 다음달 구독 연장 여부를 결정합니다.",
                        verbose_name="멤버십 활성화 여부",
                    ),
                ),
                (
                    "last_activated_at",
                    models.DateTimeField(null=True, verbose_name="최근 활성화 날짜"),
                ),
                (
                    "last_deactivated_at",
                    models.DateTimeField(null=True, verbose_name="최근 비활성화 날짜"),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성 날짜"),
                ),
                (
                    "updated_on",
                    models.DateTimeField(auto_now=True, verbose_name="최근 정보 변경 날짜"),
                ),
                (
                    "member",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="membership",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="멤버십 정보",
                    ),
                ),
            ],
            options={
                "verbose_name": "멤버십 정보",
                "verbose_name_plural": "멤버십 정보",
                "ordering": ["-id"],
            },
        ),
    ]
