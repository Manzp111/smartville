import random
import string
from account.models import OTP, User
import random


def generate_otp(user, purpose):    
    code = str(random.randint(100000, 999999)) 
    
    otp = OTP.objects.create(user=user, code=code, purpose=purpose)
    
    return otp

from rest_framework.views import exception_handler

def generate_reset_otp(user: User) -> OTP:
    """
    Generate a 6-digit OTP for password reset.
    """
    code = ''.join(random.choices(string.digits, k=6))
    otp = OTP.objects.create(user=user, code=code, purpose='reset')
    return otp

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize response
        data = {
            "success": False,
            "message": ""
        }
        if isinstance(response.data, dict) and "detail" in response.data:
            data["message"] = response.data["detail"]
        else:
            data["message"] = response.data
        response.data = data

    return response
