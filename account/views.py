from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, OTPVerifySerializer,ResendOTPSerializer
from .utils import generate_otp
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db import transaction



@extend_schema(
    request=RegisterSerializer,
    responses={
        201: OpenApiExample(
            'Account Created',
            value={
                "message": "Account created. Verify your email using the OTP.",
                "email": "user@example.com"
            },
            summary="Account successfully created"
        ),
        400: OpenApiExample(
            'Validation Error',
            value={
                "password": ["Passwords do not match."],
                "email": ["Email exist."]
            },
            summary="Validation errors"
        )
    },
    description="Create a new user account. Returns a message to verify email using OTP.",
    summary="Register to be a user of system",
)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # everything (User + Person + OTP + Email) happens inside serializer
            return Response({
                "message": "Account created. Verify your email using the OTP.",
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


                   





@extend_schema(
    request=OTPVerifySerializer,
    responses={
        200: OpenApiExample(
            'Success Response',
            value={"message": "Email verified successfully"},
            summary='OTP verification successful'
        ),
        400: OpenApiExample(
            'Error Response',
            value={"non_field_errors": ["Invalid or expired OTP"]},
            summary='OTP verification failed'
        )
    },
    description="Verify a user's email using a one-time password (OTP). If OTP is valid and not expired, the user's `is_verified` flag is set to True.",
    summary=" verify E-mail",
)
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email verified successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@extend_schema(
    request=ResendOTPSerializer,
    responses={
        200: OpenApiExample(
            "OTP Sent",
            value={"message": "A new OTP has been sent to your email."},
            summary="Successfully resent OTP"
        ),
        400: OpenApiExample(
            "Validation Error",
            value={"email": ["No user found with this email."]},
            summary="Validation or resend cooldown error"
        )
    },
    description="Resend a verification OTP to a user's email",
    summary="Resend verification OTP"
)
class ResendOTPView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
