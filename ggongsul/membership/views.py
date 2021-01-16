from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from ggongsul.membership.models import Membership
from ggongsul.membership.serializers import SubscribeSerializer, UnsubscribeSerializer


class MembershipViewSet(GenericViewSet):
    queryset = Membership.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "subscribe":
            return SubscribeSerializer
        if self.action == "unsubscribe":
            return UnsubscribeSerializer
        return None

    @action(detail=False, methods=["post"], url_path="subscribe")
    def subscribe(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @action(detail=False, methods=["post"], url_path="unsubscribe")
    def unsubscribe(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
