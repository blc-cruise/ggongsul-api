# Generated by Django 3.1.3 on 2020-12-25 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0004_memberdetail_channel_in"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="memberdetail",
            options={"verbose_name": "사용자 상세 정보", "verbose_name_plural": "사용자 상세 정보"},
        ),
    ]
