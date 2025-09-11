# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import OTP

User = get_user_model()

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, help_text="User email")

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer to reset the password using OTP.
    """
    email = serializers.EmailField(
        required=True,
        help_text="The email of the user requesting password reset"
    )
    otp = serializers.CharField(
        max_length=6,
        required=True,
        help_text="OTP code sent to the user's email"
    )
    new_password = serializers.CharField(
        min_length=8,
        write_only=True,
        required=True,
        help_text="New password for the user"
    )

