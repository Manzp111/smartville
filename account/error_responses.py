from rest_framework.response import Response
from rest_framework import status

def errorss__response(message=None, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response.
    Extracts the most relevant DRF serializer error message automatically.
    """

    def get_most_relevant_error(err_dict):
        """
        Recursively traverse nested DRF errors to find the first meaningful message.
        Prioritizes 'message' key if present.
        """
        if isinstance(err_dict, dict):
            # Prioritize 'message' key if exists
            if "message" in err_dict and err_dict["message"]:
                val = err_dict["message"]
                if isinstance(val, list) and val:
                    return str(val[0])
                elif isinstance(val, str):
                    return val
            # Otherwise, traverse all keys
            for value in err_dict.values():
                msg = get_most_relevant_error(value)
                if msg:
                    return msg
        elif isinstance(err_dict, list) and err_dict:
            return str(err_dict[0])
        elif isinstance(err_dict, str):
            return err_dict
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
