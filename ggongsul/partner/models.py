from __future__ import annotations

import os
import secrets
import uuid
import logging

from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from django.db.models import Avg

from ggongsul.core.exceptions import CommError

logger = logging.getLogger(__name__)


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
    detail: PartnerDetail
    agreement: PartnerAgreement

    name = models.CharField(max_length=32, verbose_name=_("업체 상호명"))
    address = models.CharField(max_length=128, verbose_name=_("업체 주소"))
    contact_name = models.CharField(max_length=16, verbose_name=_("대표 이름"))
    contact_phone = models.CharField(max_length=16, verbose_name=_("대표 연락처"))

    is_active = models.BooleanField(default=False, verbose_name=_("업체 활성화 여부"))

    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, verbose_name=_("경도")
    )
    latitude = models.DecimalField(
        max_digits=8, decimal_places=6, null=True, verbose_name=_("위도")
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("업체 정보")
        verbose_name_plural = _("업체 정보")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def avg_review_rating(self) -> float:
        aggregated = self.reviews.all().aggregate(Avg("rating_score"))[
            "rating_score__avg"
        ]
        return aggregated if aggregated else 0.0

    def total_review_cnt(self) -> int:
        return len(self.reviews.all())

    def detail_update_url(self) -> str:
        from django.conf import settings

        return f"{settings.BASE_URL}/partner/detail?token={self.detail.secret_token}"

    def policy_agree_yn(self) -> bool:
        if not hasattr(self, "agreement"):
            return False
        return self.agreement.policy_agreed_at is not None

    avg_review_rating.short_description = "리뷰 평점"
    total_review_cnt.short_description = "전체 리뷰 수"
    detail_update_url.short_description = "상세 정보 입력 url"
    policy_agree_yn.short_description = "이용약관 동의 여부"
    policy_agree_yn.boolean = True


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
        verbose_name = _("업체 분류")
        verbose_name_plural = _("업체 분류")


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
    class OfferType(models.IntegerChoices):
        ONE_TO_ONE = 1, _("한 명당 한병")
        TWO_TO_ONE = 2, _("두 명당 한병")
        UNLIMITED = 3, _("무제한 제공")

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
        verbose_name=_("매장 분류"),
        help_text=_("해당 업체의 카테고리입니다."),
    )
    offer_type = models.IntegerField(
        choices=OfferType.choices,
        default=OfferType.ONE_TO_ONE,
        verbose_name=_("술 제공 유형"),
        help_text=_("추후 언제든지 변경 가능합니다."),
    )

    store_phone = models.CharField(
        max_length=16, verbose_name=_("매장 전화번호"), help_text=_("예) 02-1010-2020")
    )
    short_desc = models.CharField(
        max_length=64,
        verbose_name=_("간단 매장 설명"),
        help_text=_("예) 벌집껍데기 구워주는 곳, 레트로 감성 맛집"),
    )
    detail_desc = models.TextField(
        verbose_name=_("상세 매장 설명"),
        help_text=_(
            "예) 트랜디한 레트로감성 용범이네 인계동껍데기!! 벌집껍데기를 비롯하여 항정살껍데기가 추천메뉴(대표메뉴)입니다. "
            "비빔국수와 함께 드시면 더욱더 환상적인 맛을 느끼실 수 있습니다."
        ),
    )
    ext_close_info = models.CharField(
        blank=True,
        null=True,
        max_length=128,
        verbose_name=_("매장 추가 휴무 정보"),
        help_text=_("예) 매주 월요일 휴무, 일요일 10시 마감"),
    )
    open_time = models.TimeField(
        blank=True, null=True, default=None, verbose_name=_("오픈시간")
    )
    end_time = models.TimeField(
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
    img_price_1 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 가격표(메뉴판) 사진 01"),
    )
    img_price_2 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 가격표(메뉴판) 사진 02"),
    )
    img_price_3 = models.ImageField(
        null=True,
        blank=True,
        upload_to=PathAndRename("/image/partner/"),
        verbose_name=_("업체 가격표(메뉴판) 사진 03"),
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


class PartnerAgreement(models.Model):
    partner = models.OneToOneField(
        Partner,
        on_delete=models.CASCADE,
        related_name="agreement",
        verbose_name=_("동의서"),
    )
    policy_agreed_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("정책 동의 날짜")
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("생성 날짜"))
    updated_on = models.DateTimeField(auto_now=True, verbose_name=_("최근 정보 변경 날짜"))

    class Meta:
        verbose_name = _("이용약관 동의서")
        verbose_name_plural = _("이용약관 동의서")

    def __str__(self):
        return self.partner.name + " 이용약관 동의서"

    def __repr__(self):
        return self.__str__()
