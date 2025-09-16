from rest_framework.response import Response
from rest_framework import status

def errorss__response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response.
    Safely extracts the most relevant DRF serializer error message.
    """

    def get_most_relevant_error(err):
        if isinstance(err, dict):
            for value in err.values():
                msg = get_most_relevant_error(value)
                if msg:
                    return msg
        elif isinstance(err, list) and err:
            return get_most_relevant_error(err[0])
        elif isinstance(err, str):
            return err
        return None

    if errors and not message:
        message = get_most_relevant_error(errors) or "An error occurred"
    elif not message:
        message = "An error occurred"

    response = {
        "success": False,
        "message": message,
        "errors": errors
    }

    return Response(response, status=status_code)
