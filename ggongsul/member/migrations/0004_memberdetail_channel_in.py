# Generated by Django 3.1.3 on 2020-12-25 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("member", "0003_memberagreement"),
    ]

    operations = [
        migrations.AddField(
            model_name="memberdetail",
            name="channel_in",
            field=models.IntegerField(
                choices=[
                    (1, "지인 추천"),
                    (2, "페북,인스타 광고"),
                    (3, "블로그"),
                    (4, "각종 커뮤니티"),
                    (5, "기타"),
                ],
                default=5,
                verbose_name="유입 채널",
            ),
        ),
    ]
