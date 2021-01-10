from rest_framework import serializers

from ggongsul.member.serializers import MemberSerializer
from ggongsul.partner.serializers import PartnerShortInfoSerializer
from ggongsul.visitation.models import Visitation


class VisitationSerializer(serializers.ModelSerializer):
    def validate(self, attrs: dict):
        attrs["member"] = self.context["request"].user
        return attrs

    class Meta:
        model = Visitation
        fields = ["id", "partner", "member"]
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
