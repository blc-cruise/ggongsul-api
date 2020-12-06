import logging

from django.shortcuts import render

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView

from ggongsul.member import services
from ggongsul.core.decorators import api_status_response
from ggongsul.member.models import Member

logger = logging.getLogger(__name__)


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


class MemberList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "member_list.html"

    def get(self, request: Request):
        queryset = Member.objects.all()
        logger.debug(queryset)
        return Response({"members": queryset})
