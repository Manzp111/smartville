from django.urls import path
from .views import RegisterView,OTPVerifyView,ResendOTPView,AdminUserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify_email/', OTPVerifyView.as_view(), name='verify-otp'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),


] + router.urls
