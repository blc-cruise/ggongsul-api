import logging

from django.http import HttpResponseBadRequest, HttpResponseRedirect

from django.shortcuts import get_object_or_404, resolve_url
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import (
    TemplateHTMLRenderer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PartnerDetail
from .serializers import PartnerDetailSerializer


logger = logging.getLogger(__name__)


class PartnerDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    parser_classes = [MultiPartParser, FormParser]
    template_name = "partner/partner_detail.html"

    def get(self, request: Request):
        secret_token = request.query_params.get("token", None)
        if not secret_token:
            return HttpResponseBadRequest("there is no token!")

        partner_detail: PartnerDetail = get_object_or_404(
            PartnerDetail, secret_token=secret_token
        )
        serializer = PartnerDetailSerializer(partner_detail)

        return Response(
            {
                "partner_detail": partner_detail,
                "serializer": serializer,
                "style": {"template_pack": "rest_framework/vertical"},
            }
        )

    def post(self, request: Request):
        secret_token = request.query_params.get("token", None)
        if not secret_token:
            return HttpResponseBadRequest("there is no token!")

        partner_detail: PartnerDetail = get_object_or_404(
            PartnerDetail, secret_token=secret_token
        )
        serializer = PartnerDetailSerializer(partner_detail, data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "serializer": serializer,
                    "partner_detail": partner_detail,
                    "style": {"template_pack": "rest_framework/vertical"},
                }
            )
        serializer.save()

        return HttpResponseRedirect(
            resolve_url("partner-detail") + f"?token={partner_detail.secret_token}"
        )
