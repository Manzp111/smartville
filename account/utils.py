# accounts/utils.py
import random
from .models import OTP

def generate_otp(user, purpose):    
    code = str(random.randint(100000, 999999)) 
    
    otp = OTP.objects.create(user=user, code=code, purpose=purpose)
    
    return otp

from rest_framework.views import exception_handler

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
