from django.urls import path
from .views import RegisterView,OTPVerifyView,ResendOTPView,AdminUserViewSet
from .jwt_views  import CustomTokenObtainPairView,CustomTokenRefreshView
from .password_views import PasswordResetRequestView, PasswordResetView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_email/', OTPVerifyView.as_view(), name='verify-otp'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetView.as_view(), name='password-reset-confirm'),



] + router.urls
