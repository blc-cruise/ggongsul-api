from django.urls import path
from . import views

urlpatterns = [path("detail", views.PartnerDetailView.as_view(), name="partner-detail")]
