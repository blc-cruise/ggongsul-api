from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from ggongsul.agreement.models import Agreement
from ggongsul.agreement.serializers import (
    AgreementFullSerializer,
    AgreementShortSerializer,
)


class AgreementViewSet(ReadOnlyModelViewSet):
    queryset = Agreement.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return AgreementShortSerializer
        return AgreementFullSerializer
