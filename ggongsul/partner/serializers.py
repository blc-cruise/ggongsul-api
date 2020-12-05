from rest_framework import serializers

from .models import PartnerDetail


class PartnerDetailSerializer(serializers.ModelSerializer):
    class Meta:

        model = PartnerDetail
        exclude = ["secret_token", "created_on", "updated_on", "partner"]
