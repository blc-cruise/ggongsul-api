# Generated by Django 3.1.3 on 2021-01-16 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("community", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="deleted_on",
            field=models.DateTimeField(blank=True, null=True, verbose_name="삭제 날짜"),
        ),
        migrations.AlterField(
            model_name="post",
            name="deleted_on",
            field=models.DateTimeField(blank=True, null=True, verbose_name="삭제 날짜"),
        ),
    ]
