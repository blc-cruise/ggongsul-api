import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from ggongsul.core.generics import PublicAPIView

from .serializers import LoginSerializer, SignupSerializer, CheckUsernameSerializer

logger = logging.getLogger(__name__)


class LoginView(PublicAPIView):
    serializer_class = LoginSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class SignupView(PublicAPIView):
    serializer_class = SignupSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class CheckUsernameView(PublicAPIView):
    serializer_class = CheckUsernameSerializer

    def post(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({}, status=status.HTTP_204_NO_CONTENT)
