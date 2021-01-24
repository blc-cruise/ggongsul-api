from typing import List

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ggongsul.member.serializers import MemberSerializer
from ggongsul.review.models import Review, ReviewImage
from ggongsul.visitation.models import Visitation


class ReviewSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        visitation: Visitation = attrs["visitation"]
        partner = attrs["partner"]
        member = attrs["member"] = self.context["request"].user

        if visitation.partner.pk != partner.pk or visitation.member.pk != member.pk:
            raise ValidationError(_("데이터 정합성 검증에 실패하였습니다."))

        return attrs

    class Meta:
        model = Review
        fields = [
            "id",
            "member",
            "partner",
            "visitation",
            "rating_score",
            "body",
            "images",
        ]
        extra_kwargs = {
            "visitation": {"required": True, "allow_null": False},
            "partner": {"required": True, "allow_null": False},
            "member": {"required": False, "allow_null": True},
        }


class ReviewInfoSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    member = serializers.SerializerMethodField()

    def get_images(self, obj: Review):
        images = []
        for img in obj.images.all():
            images.append(img.image.url)
        return images

    def get_member(self, obj: Review):
        if not obj.member or not obj.member.is_active:
            return "탈퇴한 회원"
        return MemberSerializer(obj.member).data

    def validate(self, attrs: dict):
        images: List[ReviewImage] = attrs["images"]
        for ri in images:
            if ri.review is not None:
                raise ValidationError(
                    _(f"review image {ri.id} 는 이미 리뷰에 등록되어있는 image 입니다.")
                )

        return attrs

    class Meta:
        model = Review
        fields = [
            "id",
            "member",
            "partner",
            "rating_score",
            "body",
            "images",
            "created_on",
        ]


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = [
            "id",
            "image",
        ]
