from rest_framework.response import Response
from rest_framework import status

def errorss__response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response.
    Extracts the first DRF serializer error message automatically.
    """
    if errors and not message:
        # Flatten nested DRF errors and get the first message
        def get_first_error(err_dict):
            if isinstance(err_dict, dict):
                for value in err_dict.values():
                    msg = get_first_error(value)
                    if msg:
                        return msg
            elif isinstance(err_dict, list) and err_dict:
                # DRF ErrorDetail objects have string representation
                return str(err_dict[0])
            elif isinstance(err_dict, str):
                return err_dict
            return None

        message = get_first_error(errors) or "An error occurred"

    elif not message:
        message = "An error occurred"

    response = {
        "success": False,
        "message": message,
        "errors": errors
    }

    return Response(response, status=status_code)
