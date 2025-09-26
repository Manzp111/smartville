from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from .jwt_serializers import CustomTokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from event.utils import success_response
from .error_responses import errorss__response


# -----------------------------
# Custom Token Obtain (Login)
# -----------------------------
TAG = ["Authentication"]

@extend_schema(
    request=CustomTokenObtainPairSerializer,
    summary="User Login using phone number with JWT authentication",
    examples=[
        OpenApiExample(
            "Login Example",
            value={
                "phone_number": "0788730366",
                "password": "Ng112233@"
            },
            request_only=True,
            summary="Example login payload"
        ),
        OpenApiExample(
            "Login Success Response",
            value={
                "status": "success",
                "message": "Login successful",
                "data": {
                    "access": "<access_token>",
                    "refresh": "<refresh_token>",
                    "user": {
                        "id": 1,
                        "phone_number": "0788730366",
                        "role": "resident"
                    }
                }
            },
            response_only=True,
            summary="Example successful login response"
        ),
        OpenApiExample(
            "Phone Not Verified",
            value={
                "status": "error",
                "message": "Phone number not verified"
            },
            response_only=True,
            summary="Response if phone number is not verified"
        )
    ]
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data,status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return errorss__response(errors=e.detail)

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
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response({
                "status": "success",
                "message": "Token refreshed successfully",
                "data": serializer.validated_data
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                "status": "error",
                "message": "Invalid refresh token"
            }, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status, permissions
from .jwt_serializers import CustomTokenObtainPairSerializer, UserSerializer
from rest_framework.views import APIView


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({
            "status": "success",
            "message": "User profile retrieved",
            "data": serializer.data
        }, status=status.HTTP_200_OK)