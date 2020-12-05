from django.urls import path

from ggongsul.member import views

urlpatterns = [path("all", views.MemberList.as_view())]
