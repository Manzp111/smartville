# accounts/views.py
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .password_serializers import PasswordResetRequestSerializer, PasswordResetSerializer
from .models import OTP
from .tasks import send_password_reset_email
import random

User = get_user_model()


class PasswordResetRequestView(APIView):
    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: OpenApiExample(
                name="Success",
                summary="OTP sent to email",
                value={"success": True, "message": "OTP has been sent to your email."},
            ),
        },
        examples=[
            OpenApiExample(
                name="Request Example",
                summary="Requesting OTP",
                value={"email": "gilbertnshimyimana11@gmail.com"},
                request_only=True
            ),
        ],
        description="Request a password reset OTP. If email exists, an OTP is sent to the user's email.",
        summary="Request password reset OTP"    
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always return success to prevent email enumeration
            return Response(
                {"success": True, "message": "If this email exists, an OTP has been sent."},
                status=status.HTTP_200_OK
            )

        code = f"{random.randint(100000, 999999)}"
        OTP.objects.create(user=user, code=code, purpose="reset")

        # Send OTP via Celery
        send_password_reset_email.delay(user.email, code)

        return Response(
            {"success": True, "message": "OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )


class PasswordResetView(APIView):
    @extend_schema(
        request=PasswordResetSerializer,
        responses={
            200: OpenApiExample(
                name="Success",
                summary="Password reset success",
                value={"success": True, "message": "Password has been reset successfully."},
            ),
            400: OpenApiExample(
                name="Failure",
                summary="Invalid OTP or user",
                value={"success": False, "message": "Invalid OTP."},
            ),
        },
        examples=[
            OpenApiExample(
                name="Request Example",
                summary="Resetting password with OTP",
                value={
                    "email": "gilbertnshimyimana11@gmail.com",
                    "otp": "123456",
                    "new_password": "Ngo123456!"
                },
                request_only=True
            ),
        ],
        description="Reset the user's password using the OTP sent to their email.",
        summary="Reset password using OTP"
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return Response({"success": False, "message": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            otp_obj = OTP.objects.get(user=user, code=data["otp"], purpose="reset")
        except OTP.DoesNotExist:
            return Response({"success": False, "message": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if not otp_obj.is_valid():
            return Response({"success": False, "message": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(data["new_password"])
        user.save()
        otp_obj.delete()

        return Response({"success": True, "message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
