# Generated by Django 3.1.3 on 2021-01-31 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("membership", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="subscription",
            name="validity_days",
        ),
    ]
