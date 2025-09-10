# accounts/utils.py
import random
from .models import OTP

def generate_otp(user, purpose):
    # Generate a random 6-digit number as a string
    code = str(random.randint(100000, 999999))
    
    # Create and save the OTP object
    otp = OTP.objects.create(user=user, code=code, purpose=purpose)
    
    return otp

