from __future__ import annotations

import os
import uuid

from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from ggongsul.member.models import Member
from ggongsul.partner.models import Partner


@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance: ReviewImage, filename: str):
        ext = filename.split(".")[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        renamed_filename = f"{uid}.{ext}"
        return os.path.join(self.path, renamed_filename)


class Review(models.Model):
    class RatingScore(models.IntegerChoices):
        ONE = 1, _("⭐")
        TWO = 2, _("⭐⭐")
        THREE = 3, _("⭐⭐⭐")
        FOUR = 4, _("⭐⭐⭐⭐")
        FIVE = 5, _("⭐⭐⭐⭐⭐")

    partner = models.ForeignKey(
        Partner,
        related_name="reviews",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("업체"),
    )
    member = models.ForeignKey(
        Member,
        related_name="reviews",
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("작성자"),
    )
    body = models.TextField(verbose_name=_("본문"))
    rating_score = models.PositiveSmallIntegerField(
        choices=RatingScore.choices, verbose_name=_("별점")
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("리뷰")
        verbose_name_plural = _("리뷰")

    def __str__(self):
        return f"{self.member} 의 {self.partner} 업체 리뷰"

    def __repr__(self):
        return self.__str__()


class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review, related_name="images", null=True, on_delete=models.SET_NULL
    )
    image = models.ImageField(
        upload_to=PathAndRename("/image/review/"),
        verbose_name=_("리뷰 사진"),
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("리뷰 이미지")
        verbose_name_plural = _("리뷰 이미지")

    def __str__(self):
        return self.image.url

    def __repr__(self):
        return self.__str__()
