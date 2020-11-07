from django.urls import path

from ggongsul.member import views

urlpatterns = [
    path("login/kakao", views.login_with_kakao),
    path("login/naver", views.login_with_naver),
]
