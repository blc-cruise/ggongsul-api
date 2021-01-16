import datetime
import logging

from django.http import HttpResponseBadRequest

from django.shortcuts import get_object_or_404, resolve_url
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import (
    TemplateHTMLRenderer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import PartnerDetail, PartnerAgreement, Partner
from .serializers import (
    PartnerDetailSerializer,
    PartnerAgreementSerializer,
    PartnerMapInfoSerializer,
    PartnerShortInfoSerializer,
    PartnerDetailInfoSerializer,
)
from ..core.filters import DistanceFilterBackend

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

        # 약관 동의 체크
        agreement, created = PartnerAgreement.objects.get_or_create(
            partner=partner_detail.partner
        )
        agreement_serializer = None
        if not agreement.policy_agreed_at:
            agreement_serializer = PartnerAgreementSerializer()

        return Response(
            {
                "partner_detail": partner_detail,
                "detail_serializer": serializer,
                "agreement_serializer": agreement_serializer,
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
        # 약관 동의 체크
        agreement, created = PartnerAgreement.objects.get_or_create(
            partner=partner_detail.partner
        )

        agreement_serializer = None
        if not agreement.policy_agreed_at:
            agreement_serializer = PartnerAgreementSerializer(
                data={"policy_agree_yn": "policy_agree_yn" in request.data}
            )

        detail_serializer = PartnerDetailSerializer(partner_detail, data=request.data)

        agreement_is_valid = True
        detail_is_valid = detail_serializer.is_valid()
        if agreement_serializer:
            agreement_is_valid = agreement_serializer.is_valid()

        if not detail_is_valid or not agreement_is_valid:
            return Response(
                {
                    "partner_detail": partner_detail,
                    "detail_serializer": detail_serializer,
                    "agreement_serializer": agreement_serializer,
                    "style": {"template_pack": "rest_framework/vertical"},
                }
            )

        detail_serializer.save()
        # 약관 동의 처리
        if not agreement.policy_agreed_at:
            agreement.policy_agreed_at = datetime.datetime.now()
            agreement.save()

        return Response(
            {
                "title": "등록/수정이 완료되었습니다 :)",
                "sub_title": "* 추후 수정할일 있으시면 언제든 아래 URL링크 클릭해서 변경해주세요.",
                "url_path": f"{resolve_url('partner-detail')}?token={partner_detail.secret_token}",
            },
            template_name="partner/okay.html",
        )


class PartnerAgreementView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "partner/partner_agreement.html"

    def get(self, request: Request):
        return Response({})


class PartnerViewSet(ReadOnlyModelViewSet):
    queryset = Partner.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    search_fields = ["name"]

    @property
    def filter_backends(self):
        if self.action == "near_partners":
            return [DistanceFilterBackend]
        return [SearchFilter]

    def get_serializer_class(self):
        if self.action == "near_partners":
            return PartnerShortInfoSerializer
        elif self.action == "retrieve":
            return PartnerDetailInfoSerializer
        return PartnerMapInfoSerializer

    @action(detail=False, methods=["get"], url_path="near")
    def near_partners(self, request: Request):
        return self.list(request)
