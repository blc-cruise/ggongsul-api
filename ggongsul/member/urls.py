from django.urls import path

from ggongsul.member import views

urlpatterns = [
    path("login", views.LoginView.as_view()),
]
