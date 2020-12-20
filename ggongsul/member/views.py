import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from .serializers import LoginSerializer

logger = logging.getLogger(__name__)


class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    serializer_class = LoginSerializer
    www_authenticate_realm = "api"

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            "Bearer",
            self.www_authenticate_realm,
        )

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validate_data, status=status.HTTP_200_OK)


class SignupView(GenericAPIView):
    pass
