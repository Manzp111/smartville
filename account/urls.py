from django.urls import path
from .views import RegisterView,OTPVerifyView,ResendOTPView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', OTPVerifyView.as_view(), name='verify-otp'),
    path('resent_otp/', ResendOTPView.as_view(), name='resend-otp'),


]
