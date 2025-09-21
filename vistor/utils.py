# utils/response.py
from rest_framework.response import Response

def standard_response(data=None, message="", success=True, meta=None, status=200):
    return Response({
        "success": success,
        "message": message,
        "data": data,
        "meta": meta or {}
    }, status=status)
