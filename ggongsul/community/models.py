from __future__ import annotations

import os
import uuid

from django.db import models
from django.utils.deconstruct import deconstructible

from ggongsul.member.models import Member
from django.utils.translation import gettext_lazy as _


@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance: Post, filename: str):
        ext = filename.split(".")[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        renamed_filename = f"{instance.member.id}/{uid}.{ext}"
        return os.path.join(self.path, renamed_filename)


class Post(models.Model):
    member = models.ForeignKey(
        Member,
        related_name="posts",
        on_delete=models.CASCADE,
        verbose_name=_("사용자"),
    )
    body = models.TextField(verbose_name=_("본문"))
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/post/"),
        verbose_name=_("이미지"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, verbose_name=_("경도")
    )
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, null=True, verbose_name=_("위도")
    )

    is_deleted = models.BooleanField(default=False, verbose_name=_("삭제 여부"))
    deleted_on = models.DateTimeField(null=True, verbose_name=_("삭제 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.member.username} 의 포스트 {self.id}"

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("게시글")
        verbose_name_plural = _("게시글")

    def total_attention_cnt(self):
        return len(self.attentions.filter(is_deleted=False).all())

    def total_comment_cnt(self):
        return len(self.comments.filter(is_deleted=False).all())

    def short_body(self):
        return self.body

    total_attention_cnt.short_description = "전체 좋아요 수"
    total_comment_cnt.short_description = "전체 댓글 수"


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("게시글"),
    )
    member = models.OneToOneField(
        Member,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name=_("사용자"),
    )
    body = models.CharField(max_length=64, verbose_name=_("본문"))

    is_deleted = models.BooleanField(default=False, verbose_name=_("삭제 여부"))
    deleted_on = models.DateTimeField(null=True, verbose_name=_("삭제 날짜"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.member.username} 의 포스트 {self.post.id} 의 댓글 {self.id}"

    class Meta:
        ordering = ["-created_on"]
        verbose_name = _("댓글")
        verbose_name_plural = _("댓글")


class Attention(models.Model):
    post = models.ForeignKey(
        Post,
        related_name="attentions",
        on_delete=models.CASCADE,
        verbose_name=_("게시글"),
    )
    member = models.ForeignKey(
        Member,
        related_name="attentions",
        on_delete=models.CASCADE,
        verbose_name=_("사용자"),
    )

    is_deleted = models.BooleanField(default=False, verbose_name=_("삭제 여부"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        ordering = ["-id"]
        unique_together = (
            "post",
            "member",
        )
        verbose_name = _("관심")
        verbose_name_plural = _("관심")
