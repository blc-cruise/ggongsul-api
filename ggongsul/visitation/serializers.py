from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ggongsul.member.serializers import MemberSerializer
from ggongsul.partner.models import Partner
from ggongsul.partner.serializers import PartnerShortInfoSerializer
from ggongsul.visitation.models import Visitation


class VisitationSerializer(serializers.ModelSerializer):
    cert_num = serializers.CharField(
        required=True, allow_null=False, max_length=10, write_only=True
    )

    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user

        # partner password validation
        partner: Partner = attrs["partner"]
        if not partner.is_active:
            raise ValidationError(_("활성화 되지 않은 업체입니다."))

        cert_num = attrs["cert_num"]
        if partner.cert_num != cert_num:
            raise ValidationError(_("인증번호가 일치하지 않습니다."))
        del attrs["cert_num"]

        return attrs

    class Meta:
        model = Visitation
        fields = ["id", "partner", "member", "cert_num"]
        extra_kwargs = {
            "partner": {"required": True, "allow_null": False},
            "member": {"required": True, "allow_null": False, "write_only": True},
        }


class VisitationInfoSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    partner = PartnerShortInfoSerializer(read_only=True)

    class Meta:
        model = Visitation
        fields = ["id", "member", "partner", "is_reviewed", "created_on"]
