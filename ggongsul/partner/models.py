from __future__ import annotations

import os
import secrets
import uuid

from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


# Create your models here.
from ggongsul.core.exceptions import CommError


@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance: PartnerDetail, filename: str):
        ext = filename.split(".")[-1]  # eg: 'jpg'
        uid = uuid.uuid4().hex[:10]  # eg: '567ae32f97'

        renamed_filename = f"{instance.partner.id}/{uid}.{ext}"
        return os.path.join(self.path, renamed_filename)


class Partner(models.Model):
    name = models.CharField(max_length=32, verbose_name=_("업체 상호명"))
    address = models.CharField(max_length=128, verbose_name=_("업체 주소"))
    contact_name = models.CharField(max_length=16, verbose_name=_("대표 이름"))
    contact_phone = models.CharField(max_length=16, verbose_name=_("대표 연락처"))

    is_active = models.BooleanField(default=False, verbose_name=_("업체 활성화 여부"))

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("업체 정보")
        verbose_name_plural = _("업체 정보")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class PartnerCategory(models.Model):
    name = models.CharField(
        max_length=10, verbose_name=_("카테고리 이름"), help_text=_("업체를 분류할 카테고리 이름입니다.")
    )
    icon_img = models.ImageField(
        default="/image/category/default.png",
        verbose_name=_("카테고리 이미지"),
        help_text=_("카테고리를 표현할 간단한 이미지입니다."),
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = _("카테고리")
        verbose_name_plural = _("카테고리")


class PartnerDetailManager(models.Manager):
    def create(self, **obj_data):
        token_str = secrets.token_hex(16)
        retry_cnt = 0

        while self.filter(secret_token=token_str).exists():
            if retry_cnt > 5:
                raise CommError("Secret token generation failed")

            token_str = secrets.token_hex(16)
            retry_cnt += 1

        obj_data["secret_token"] = token_str
        return super().create(**obj_data)


class PartnerDetail(models.Model):
    partner = models.OneToOneField(
        Partner, on_delete=models.CASCADE, related_name="detail", verbose_name=_("업체")
    )
    secret_token = models.CharField(
        max_length=32, unique=True, verbose_name=_("업체 관리용 비밀 토큰")
    )
    category = models.ForeignKey(
        PartnerCategory,
        null=True,
        on_delete=models.SET_NULL,
        related_name="partners",
        verbose_name=_("카테고리"),
        help_text=_("해당 업체의 카테고리입니다."),
    )

    store_phone = models.CharField(max_length=16, verbose_name=_("매장 연락처"))
    short_desc = models.CharField(max_length=64, verbose_name=_("한 줄 소개"))
    detail_desc = models.TextField(verbose_name=_("상세 소개"))
    ext_close_info = models.CharField(
        blank=True,
        null=True,
        max_length=128,
        verbose_name=_("추가 휴무 정보"),
        help_text=_("업체의 추가 휴무정보를 입력합니다."),
    )
    open_time = models.DateTimeField(
        blank=True, null=True, default=None, verbose_name=_("오픈시간")
    )
    end_time = models.DateTimeField(
        blank=True, null=True, default=None, verbose_name=_("마감시간")
    )

    img_main = models.ImageField(
        default="/image/partner/default.png",
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 대표 이미지"),
        help_text=_("업체의 대표 이미지입니다."),
    )

    img_store_1 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 매장 사진 01"),
    )
    img_store_2 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 매장 사진 02"),
    )
    img_store_3 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 매장 사진 03"),
    )
    img_store_4 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 매장 사진 04"),
    )
    img_store_5 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 매장 사진 05"),
    )

    img_menu_1 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 메뉴 사진 01"),
    )
    img_menu_2 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 메뉴 사진 02"),
    )
    img_menu_3 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 메뉴 사진 03"),
    )
    img_menu_4 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 메뉴 사진 04"),
    )
    img_menu_5 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 메뉴 사진 05"),
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    objects = PartnerDetailManager()

    class Meta:
        verbose_name = _("업체 상세 정보")
        verbose_name_plural = _("업체 상세 정보")

    def __str__(self):
        return self.partner.name + " 상세 정보"

    def __repr__(self):
        return self.__str__()
