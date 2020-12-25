from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ggongsul.partner import views as partner_views
from ggongsul.agreement import views as agreement_views
from ggongsul.review import views as review_views


v1_router = DefaultRouter()
v1_router.register("partners", partner_views.PartnerViewSet)
v1_router.register("agreements", agreement_views.AgreementViewSet)
v1_router.register("reviews", review_views.ReviewViewSet)


urlpatterns = [
    path("v1/", include(v1_router.urls)),
]
