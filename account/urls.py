from django.urls import path
from .views import RegisterView,OTPVerifyView,ResendOTPView,AdminUserViewSet
from .jwt_views  import CustomTokenObtainPairView,CustomTokenRefreshView,MeView
from .password_views import PasswordResetRequestView, PasswordResetView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'smartvillage/admin', AdminUserViewSet, basename='admin-users')


urlpatterns = [
    path('user/register/', RegisterView.as_view(), name='register'),
    path('user/verify_email/', OTPVerifyView.as_view(), name='verify-otp'),
    path('user/resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path("user/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("user/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path('user/password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('user/password-reset/confirm/', PasswordResetView.as_view(), name='password-reset-confirm'),
     path("me/", MeView.as_view(), name="user_profile"),



] + router.urls
