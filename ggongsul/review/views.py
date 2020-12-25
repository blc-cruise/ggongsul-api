from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django_filters.rest_framework import DjangoFilterBackend

from ggongsul.review.models import Review
from ggongsul.review.serializers import ReviewSerializer, ReviewImageSerializer


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["partner", "member"]

    def get_serializer_class(self):
        if self.action == "upload_image":
            return ReviewImageSerializer
        return ReviewSerializer

    @action(detail=False, methods=["post"], url_path="upload-image")
    def upload_image(self, request: Request):
        return self.create(request)
