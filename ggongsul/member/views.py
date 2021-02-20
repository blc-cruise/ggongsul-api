import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ggongsul.core.generics import PublicAPIView

from .serializers import (
    LoginSerializer,
    SignupSerializer,
    CheckUsernameSerializer,
    MemberSerializer,
    MemberProfileImageSerializer,
    UpdateProfileImageSerializer,
)
from .models import Member

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


class MemberViewSet(GenericViewSet):
    queryset = Member.objects.filter(is_active=True)

    @property
    def permission_classes(self):
        if self.action == "upload_profile_image":
            return [AllowAny]
        return [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "get_me_info":
            return MemberSerializer
        elif self.action == "upload_profile_image":
            return MemberProfileImageSerializer
        elif self.action == "update_profile_image":
            return UpdateProfileImageSerializer
        return None

    @action(detail=False, methods=["post"], url_path="upload-profile-image")
    def upload_profile_image(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="update-profile-image")
    def update_profile_image(self, request: Request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me")
    def get_me_info(self, request: Request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="me/deactivate")
    def deactivate_me_info(self, request: Request):
        me: Member = request.user
        me.is_active = False
        me.save()
        return Response({"message": "okay"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/billing-key")
    def get_billing_key(self, request: Request):
        member = request.user
        if not member.is_billing_key_exist():
            raise NotFound({"suggested_billing_key": member.billing_key})

        return Response({"billing_key": member.billing_key}, status=status.HTTP_200_OK)
