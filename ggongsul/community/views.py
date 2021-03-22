from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import Serializer

from ggongsul.community.models import Post, Comment, Attention
from ggongsul.community.serializers import (
    PostShortInfoSerializer,
    PostDetailInfoSerializer,
    PostSerializer,
    CommentSerializer,
    CommentInfoSerializer,
    PostImageSerializer,
)
from ggongsul.core.filters import PostFilterBackend
from ggongsul.core.paginations import SmallResultsSetPagination
from ggongsul.core.permissions import IsObjectOwnerMember


class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(is_deleted=False)
    pagination_class = SmallResultsSetPagination
    ordering = ("-created_on",)

    @property
    def filter_backends(self):
        if self.action == "list":
            return [OrderingFilter]
        return []

    @property
    def permission_classes(self):
        if self.action == "destroy":
            return [IsObjectOwnerMember]
        if self.action == "update":
            return [IsObjectOwnerMember]
        return [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return PostShortInfoSerializer
        if self.action == "retrieve":
            return PostDetailInfoSerializer
        if self.action == "tab_attention":
            return Serializer
        if self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    def perform_destroy(self, instance: Post):
        cur_datetime = timezone.now()
        instance.is_deleted = True
        instance.deleted_on = cur_datetime
        instance.save()

    @action(detail=True, methods=["post"], url_path="tab")
    def tab_attention(self, request: Request, pk=None):
        post: Post = self.get_object()
        member = request.user

        attention, created = Attention.objects.get_or_create(post=post, member=member)
        if not created:
            # true if false, false if true
            attention.is_deleted = not (attention.is_deleted or False)
            attention.save()

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="upload-image")
    def upload_image(self, request: Request):
        return self.create(request)


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.filter(is_deleted=False)
    filter_backends = (PostFilterBackend,)
    post_look_up_keyword = "post_id"

    @property
    def permission_classes(self):
        if self.action in ["destroy", "update"]:
            return [IsObjectOwnerMember]
        return [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CommentInfoSerializer
        return CommentSerializer

    def perform_destroy(self, instance: Comment):
        cur_datetime = timezone.now()
        instance.is_deleted = True
        instance.deleted_on = cur_datetime
        instance.save()
