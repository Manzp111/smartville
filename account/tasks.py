# accounts/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import OTP

@shared_task
def send_verification_email_task(email, otp_code):
    subject = "Verify your email"
    message = f"Hello {email},\n\nUse the following OTP to verify your email: {otp_code}\n\nThis OTP expires in 30 minutes."
    from_email = "no-reply@example.com"
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def cleanup_otps():
    # Delete used OTPs
    OTP.objects.filter(is_used=True).delete()
    
    # Delete expired OTPs
    from django.utils import timezone
    import pytz
    from datetime import timedelta

    now = timezone.now().astimezone(pytz.timezone('Africa/Kigali'))
    expired_otps = OTP.objects.filter(created_at__lt=now - timedelta(minutes=30))
    expired_otps.delete()
    
    return f"Deleted {expired_otps.count()} expired OTPs"

