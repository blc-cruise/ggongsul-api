# Generated by Django 3.1.3 on 2020-12-20 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="first_name",
        ),
        migrations.RemoveField(
            model_name="member",
            name="last_name",
        ),
        migrations.CreateModel(
            name="MemberDetail",
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
                    "member",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="detail",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="멤버",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SocialAccount",
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
                    "provider",
                    models.CharField(
                        choices=[("kakao", "카카오")],
                        max_length=20,
                        verbose_name="소셜 인증 제공 업체",
                    ),
                ),
                ("uid", models.CharField(max_length=120, verbose_name="소셜 인증 Id")),
                (
                    "unlink_yn",
                    models.BooleanField(default=False, verbose_name="소셜 계정 연결 여부"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="생성 날짜"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="최근 정보 변경 날짜"),
                ),
                (
                    "member",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_accounts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
            ],
            options={
                "verbose_name": "소셜 계정",
                "verbose_name_plural": "소셜 계정",
                "ordering": ("-id",),
                "unique_together": {("provider", "uid")},
            },
        ),
    ]
