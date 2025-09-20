from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message="Success", status_code=200, meta=None):
    response = {
        "success": True,
        "message": message,
        "data": data or {},
    }
    if meta:
        response["meta"] = meta
    return Response(response, status=status_code)

def error_response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    if errors and not message:
        first_error_msg = next(iter(errors.values()))
        if first_error_msg:
            message = first_error_msg[0]
        else:
            message = "An error occurred"
    elif not message:
        message = "An error occurred"
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status_code)