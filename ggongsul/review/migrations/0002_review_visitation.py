# Generated by Django 3.1.3 on 2021-01-03 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("visitation", "0001_initial"),
        ("review", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="visitation",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="review",
                to="visitation.visitation",
                verbose_name="방문 기록",
            ),
        ),
    ]
