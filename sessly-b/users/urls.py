from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    LogoutView,
    MeView,
    RegisterView,
    ResendVerificationCodeView,
    VerifyEmailView,
    ToggleFavoriteView,
    UserFavoritesView
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("verify-email/resend/", ResendVerificationCodeView.as_view(), name="resend_verify_email"),
    path("favorites/", UserFavoritesView.as_view(), name="auth_register"),
    path("favorites/<int:business_id>/", ToggleFavoriteView.as_view(), name="toggle_favorite"),
]
