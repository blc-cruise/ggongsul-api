# Generated by Django 3.1.3 on 2021-01-24 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0004_auto_20210117_0938"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="address",
            field=models.CharField(max_length=64, null=True, verbose_name="주소"),
        ),
    ]