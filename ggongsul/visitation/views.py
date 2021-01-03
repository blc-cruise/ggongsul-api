from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ggongsul.core.authentications import MembershipAuthentication
from ggongsul.core.filters import MemberFilterBackend
from ggongsul.core.paginations import SmallResultsSetPagination
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
    permission_classes = [IsAuthenticated]
    filter_backends = [MemberFilterBackend, DjangoFilterBackend]
    filterset_fields = ["partner"]
    authentication_classes = [MembershipAuthentication]
    pagination_class = SmallResultsSetPagination

    def get_serializer_class(self):
        if self.action == "create":
            return VisitationSerializer
        return VisitationInfoSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(
            data={**request.data, "member": request.user.pk}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
