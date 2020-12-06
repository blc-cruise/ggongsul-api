from django.urls import path
from . import views

urlpatterns = [
    path("detail", views.PartnerDetailView.as_view(), name="partner-detail"),
    path("agreement", views.PartnerAgreementView.as_view(), name="partner-agreement"),
]
