from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ggongsul.partner import views as partner_views


v1_router = DefaultRouter()
v1_router.register("partners", partner_views.PartnerMapInfoViewSet)

urlpatterns = [path("v1/", include(v1_router.urls))]
