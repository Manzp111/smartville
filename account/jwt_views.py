# account/jwt_views.py
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .models import User
from .jwt_serializers import CustomTokenObtainPairSerializer


@extend_schema(
    request=CustomTokenObtainPairSerializer,
    summary="User Login we used JWT authentication",
    examples=[
        OpenApiExample(
            "Login Example",
            value={
                "email": "gilbertnshimyimana130@gmail.com",
                "password": "Ng112233@"
            },
            request_only=True,
            summary="Example login payload"
        ),
        OpenApiExample(
            "Login Success Response",
            value={
                "success": True,
                "message": "Login successful",
                "data": {
                    "access": "<access_token>",
                    "refresh": "<refresh_token>",
                    "user": {
                        "id": 1,
                        "email": "gilbertnshimyimana130@gmail.com",
                        "role": "resident"
                    }
                }
            },
            response_only=True,
            summary="Example successful login response"
        ),
        OpenApiExample(
            "Email Not Verified",
            value={
                "success": False,
                "message": "Email not verified"
            },
            response_only=True,
            summary="Response if email is not verified"
        )
    ],
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# -----------------------------
# Custom Token Refresh
# -----------------------------
@extend_schema(
    request=TokenRefreshSerializer,
    examples=[
        OpenApiExample(
            "Refresh Token Request",
            value={"refresh": "<refresh_token>"},
            request_only=True,
            summary="Refresh token payload"
        ),
        OpenApiExample(
            "Refresh Token Success",
            value={
                "status": "success",
                "message": "Token refreshed successfully",
                "data": {"access": "<new_access_token>"}
            },
            response_only=True,
            summary="Successful token refresh response"
        ),
        OpenApiExample(
            "Invalid Refresh Token",
            value={
                "status": "error",
                "message": "Invalid refresh token"
            },
            response_only=True,
            summary="Response if refresh token is invalid"
        )
    ]
)

@extend_schema(
    request=TokenRefreshSerializer,
    summary="Refresh JWT token",
    examples=[
        OpenApiExample(
            "Refresh Token Request",
            value={"refresh": "<refresh_token>"},
            request_only=True,
            summary="Refresh token payload"
        ),
        OpenApiExample(
            "Refresh Token Success",
            value={
                "success": True,
                "message": "Token refreshed successfully",
                "data": {"access": "<new_access_token>"}
            },
            response_only=True,
            summary="Successful token refresh response"
        ),
        OpenApiExample(
            "Invalid Refresh Token",
            value={
                "success": False,
                "message": "Invalid refresh token"
            },
            response_only=True,
            summary="Response if refresh token is invalid"
        )
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                "success": True,
                "message": "Token refreshed successfully",
                "data": serializer.validated_data
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "success": False,
                "message": "Invalid refresh token"
            }, status=status.HTTP_400_BAD_REQUEST)
