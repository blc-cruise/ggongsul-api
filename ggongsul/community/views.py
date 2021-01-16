from django.utils import timezone
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.serializers import Serializer

from ggongsul.community.models import Post, Comment, Attention
from ggongsul.community.serializers import (
    PostShortInfoSerializer,
    PostDetailInfoSerializer,
    PostSerializer,
    CommentSerializer,
)
from ggongsul.core.filters import DistanceFilterBackend
from ggongsul.core.paginations import SmallResultsSetPagination
from ggongsul.core.permissions import IsObjectOwnerMember


class PostViewSet(ModelViewSet):
    queryset = Post.objects.filter(is_deleted=False)
    pagination_class = SmallResultsSetPagination

    @property
    def filter_backends(self):
        if self.action == "list":
            return [DistanceFilterBackend]
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


class CommentViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Comment.objects.filter(is_deleted=False)
    serializer_class = CommentSerializer

    @property
    def permission_classes(self):
        if self.action == "destroy":
            return [IsObjectOwnerMember]
        if self.action == "update":
            return [IsObjectOwnerMember]
        return [IsAuthenticated]

    def perform_destroy(self, instance: Comment):
        cur_datetime = timezone.now()
        instance.is_deleted = True
        instance.deleted_on = cur_datetime
        instance.save()
