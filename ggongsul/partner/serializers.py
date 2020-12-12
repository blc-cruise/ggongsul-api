import logging

from typing import List

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import PartnerDetail, Partner

logger = logging.getLogger(__name__)


def only_true_required(value):
    if not value:
        raise serializers.ValidationError("이용약관에 동의하셔야합니다.")


class PartnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerDetail
        exclude = ["secret_token", "created_on", "updated_on", "partner"]


class PartnerAgreementSerializer(serializers.Serializer):
    policy_agree_yn = serializers.BooleanField(
        validators=[only_true_required],
        label=_("제휴점 이용약관에 동의합니다."),
    )

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PartnerMapInfoSerializer(serializers.ModelSerializer):
    offer_type = serializers.IntegerField(source="detail.offer_type")

    class Meta:
        model = Partner
        fields = ["id", "name", "longitude", "latitude", "offer_type"]


class PartnerShortInfoSerializer(serializers.ModelSerializer):
    offer_type = serializers.IntegerField(source="detail.offer_type")
    short_desc = serializers.CharField(source="detail.short_desc")
    img_main = serializers.CharField(source="detail.img_main.url")
    category = serializers.CharField(source="detail.category.name")

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "address",
            "short_desc",
            "offer_type",
            "img_main",
            "category",
        ]


class PartnerDetailInfoSerializer(serializers.ModelSerializer):
    offer_type = serializers.IntegerField(source="detail.offer_type")
    short_desc = serializers.CharField(source="detail.short_desc")
    detail_desc = serializers.CharField(source="detail.detail_desc")
    img_main = serializers.CharField(source="detail.img_main.url")
    category = serializers.CharField(source="detail.category.name")
    store_phone = serializers.CharField(source="detail.store_phone")

    open_time = serializers.TimeField(source="detail.open_time")
    end_time = serializers.TimeField(source="detail.end_time")
    ext_close_info = serializers.CharField(source="detail.ext_close_info")

    img_store_list = serializers.SerializerMethodField(read_only=True)
    img_menu_list = serializers.SerializerMethodField(read_only=True)

    def get_img_store_list(self, obj: Partner) -> List[str]:
        img_store_list = []
        detail = obj.detail

        if detail.img_store_1:
            img_store_list.append(detail.img_store_1.url)
        if detail.img_store_2:
            img_store_list.append(detail.img_store_2.url)
        if detail.img_store_3:
            img_store_list.append(detail.img_store_3.url)
        if detail.img_store_4:
            img_store_list.append(detail.img_store_4.url)
        if detail.img_store_5:
            img_store_list.append(detail.img_store_5.url)

        return img_store_list

    def get_img_menu_list(self, obj: Partner) -> List[str]:
        img_menu_list = []
        detail = obj.detail

        if detail.img_menu_1:
            img_menu_list.append(detail.img_menu_1.url)
        if detail.img_menu_2:
            img_menu_list.append(detail.img_menu_2.url)
        if detail.img_menu_3:
            img_menu_list.append(detail.img_menu_3.url)
        if detail.img_menu_4:
            img_menu_list.append(detail.img_menu_4.url)
        if detail.img_menu_5:
            img_menu_list.append(detail.img_menu_5.url)

        return img_menu_list

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "address",
            "short_desc",
            "detail_desc",
            "open_time",
            "end_time",
            "ext_close_info",
            "offer_type",
            "img_main",
            "category",
            "store_phone",
            "img_store_list",
            "img_menu_list",
        ]
