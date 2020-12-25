from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import serializers


class PublicAPIView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    www_authenticate_realm = "api"

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            "Bearer",
            self.www_authenticate_realm,
        )


class APISerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        raise Exception("API serializer dose not have update method!")

    def create(self, validated_data):
        raise Exception("API serializer dose not have create method!")
