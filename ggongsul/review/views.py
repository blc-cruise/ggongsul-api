from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend

from ggongsul.core.permissions import IsObjectOwnerMember
from ggongsul.review.models import Review
from ggongsul.review.serializers import (
    ReviewInfoSerializer,
    ReviewImageSerializer,
    ReviewSerializer,
)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.filter(is_deleted=False)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["partner", "member"]

    @property
    def permission_classes(self):
        if self.action in ["destroy", "update"]:
            return [IsObjectOwnerMember]
        return [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "upload_image":
            return ReviewImageSerializer
        if self.action in ["list", "retrieve"]:
            return ReviewInfoSerializer
        return ReviewSerializer

    def perform_destroy(self, instance: Review):
        cur_datetime = timezone.now()
        instance.is_deleted = True
        instance.deleted_on = cur_datetime
        instance.save()

    @action(detail=False, methods=["post"], url_path="upload-image")
    def upload_image(self, request: Request):
        return self.create(request)
