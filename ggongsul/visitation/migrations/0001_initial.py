# Generated by Django 3.1.3 on 2021-01-03 15:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("partner", "0006_auto_20210103_1501"),
    ]

    operations = [
        migrations.CreateModel(
            name="Visitation",
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
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="visitations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="사용자",
                    ),
                ),
                (
                    "partner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="visitations",
                        to="partner.partner",
                        verbose_name="업체",
                    ),
                ),
            ],
            options={
                "verbose_name": "방문 기록",
                "verbose_name_plural": "방문 기록",
                "ordering": ["-created_on"],
            },
        ),
    ]