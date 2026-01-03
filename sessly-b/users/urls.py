from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from businesses.customer_views import CustomerAppointmentViewSet
from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    LogoutView,
    MeView,
    RegisterView,
    ResendVerificationCodeView,
    VerifyEmailView,
    ToggleFavoriteView,
    UserFavoritesView,
)

# Router for customer appointments
router = DefaultRouter()
router.register(r'appointments', CustomerAppointmentViewSet, basename='customer-appointments')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("verify-email/resend/", ResendVerificationCodeView.as_view(), name="resend_verify_email"),
    path("favorites/", UserFavoritesView.as_view(), name="user_favorites"),
    path("favorites/<uuid:business_id>/", ToggleFavoriteView.as_view(), name="toggle_favorite"),
    path("", include(router.urls)),
]
