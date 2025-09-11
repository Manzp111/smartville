# accounts/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import OTP

from django.conf import settings

@shared_task(bind=True, max_retries=3)
def send_verification_email_task(self, first_name, last_name, email, otp_code):
    subject = "Verify your email"
    message = f"Hello {last_name}-{first_name},\n\nUse the following OTP to verify your email: {otp_code}\n\nThis OTP expires in 30 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        raise self.retry(exc=e, countdown=60)



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

@shared_task
def send_password_reset_email(email, code):
    subject = "Your Password Reset OTP"
    message = f"Use this OTP to reset your password: {code}. Valid for 10 minutes."
    send_mail(subject, message, "gilbertnshimyimana130@gmail.com", [email])
