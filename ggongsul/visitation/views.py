from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from ggongsul.core.filters import MemberFilterBackend
from ggongsul.core.paginations import SmallResultsSetPagination
from ggongsul.core.permissions import HasMembershipBenefits
from ggongsul.visitation.models import Visitation
from ggongsul.visitation.serializers import (
    VisitationSerializer,
    VisitationInfoSerializer,
)


class VisitationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Visitation.objects.all()
    filter_backends = [MemberFilterBackend, DjangoFilterBackend]
    filterset_fields = ["partner"]
    pagination_class = SmallResultsSetPagination

    @property
    def permission_classes(self):
        if self.action in ["retrieve", "list"]:
            return IsAuthenticated
        return HasMembershipBenefits

    def get_serializer_class(self):
        if self.action == "create":
            return VisitationSerializer
        return VisitationInfoSerializer

    def create(self, request: Request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
