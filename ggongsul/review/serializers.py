from typing import List

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ggongsul.review.models import Review, ReviewImage


class UrlRelatedField(serializers.RelatedField):
    default_error_messages = {
        "does_not_exist": _('Invalid pk "{pk_value}" - object does not exist.'),
        "incorrect_type": _("Incorrect type. Expected pk value, received {data_type}."),
    }

    def __init__(self, slug_field=None, **kwargs):
        assert slug_field is not None, "The `slug_field` argument is required."
        self.slug_field = slug_field
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            return queryset.get(pk=data)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=data)
        except (TypeError, ValueError):
            self.fail("incorrect_type", data_type=type(data).__name__)

    def to_representation(self, obj):
        return getattr(obj, self.slug_field).url


class ReviewSerializer(serializers.ModelSerializer):
    images = UrlRelatedField(
        many=True, slug_field="image", queryset=ReviewImage.objects.all()
    )

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
        ]


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = [
            "id",
            "image",
        ]
