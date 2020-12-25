from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from ggongsul.member import views as member_views


urlpatterns = [
    path("login", member_views.LoginView.as_view(), name="login"),
    path("signup", member_views.SignupView.as_view(), name="signup"),
    path(
        "check-username",
        member_views.CheckUsernameView.as_view(),
        name="check-username",
    ),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify", TokenVerifyView.as_view(), name="token-verify"),
]
