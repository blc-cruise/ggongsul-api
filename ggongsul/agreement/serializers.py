from rest_framework import serializers

from ggongsul.agreement.models import Agreement


class AgreementFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = ["id", "name", "body"]


class AgreementShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = ["id", "name"]
