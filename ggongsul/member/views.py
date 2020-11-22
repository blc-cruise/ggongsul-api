from django.shortcuts import render

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from ggongsul.member import services
from ggongsul.core.decorators import api_status_response


def home(request):
    return render(request, "home.html")


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@api_status_response
def login_with_kakao(request: Request):
    return services.login(request.query_params, services.LoginType.Kakao)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
@api_status_response
def login_with_naver(request: Request):
    return services.login(request.query_params, services.LoginType.Naver)
