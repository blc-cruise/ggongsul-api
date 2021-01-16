from django.db.models import F
from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt
from rest_framework import filters
from rest_framework.exceptions import ValidationError

from ggongsul.core.validators import validate_dict_key


class MemberFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(member=request.user)


class DistanceFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        lat, lng = validate_dict_key(request.query_params, ["lat", "lng"])

        if (
            not lat.replace(".", "", 1).isnumeric()
            or not lng.replace(".", "", 1).isnumeric()
        ):
            raise ValidationError(
                {"msg": "'lat' and 'lng' query params should be float!"}
            )

        lat = float(lat)
        lng = float(lng)

        num_km = getattr(view, "distance_num_km", 5)

        dlat = Radians(F("latitude") - lat)
        dlong = Radians(F("longitude") - lng)

        a = Power(Sin(dlat / 2), 2) + Cos(Radians(lat)) * Cos(
            Radians(F("latitude"))
        ) * Power(Sin(dlong / 2), 2)

        c = 2 * ATan2(Sqrt(a), Sqrt(1 - a))
        d = 6371 * c

        return (
            queryset.annotate(distance=d)
            .order_by("distance")
            .filter(distance__lt=num_km)
        )

    def get_schema_operation_parameters(self, view):
        return [
            {
                "name": "lat",
                "required": True,
                "in": "query",
                "description": "latitude",
                "schema": {
                    "type": "float",
                },
            },
            {
                "name": "lng",
                "required": True,
                "in": "query",
                "description": "longitude",
                "schema": {
                    "type": "float",
                },
            },
        ]
