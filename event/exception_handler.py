from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, ValidationError

def custom_exception_handler(exc, context):
    """
    Custom DRF exception handler to return consistent JSON responses.
    """

    # Handle JWT token errors
    if isinstance(exc, (TokenError, InvalidToken)):
        return Response(
            {
                "success": False,
                "message": "Access token expired or invalid. Please login again.",
                "errors": None
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Handle unauthenticated access
    if isinstance(exc, NotAuthenticated):
        return Response(
            {
                "success": False,
                "message": "Authentication credentials were not provided or are invalid.",
                "errors": None
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Handle permission errors
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": str(exc.detail),
                "errors": None
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Handle validation errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "errors": exc.detail
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Let DRF handle other exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize other responses
        message = response.data.get("detail", str(response.data))
        response.data = {
            "success": False,
            "message": message,
            "errors": getattr(response.data, "errors", None)
        }

    return response
