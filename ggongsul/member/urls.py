from django.urls import path

from ggongsul.member import views

urlpatterns = [
    path("login", views.LoginView.as_view()),
    path("signup", views.SignupView.as_view()),
]
