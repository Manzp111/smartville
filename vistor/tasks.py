# visitors/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_new_visitor_email(leader_email, visitor_name, host_name, village_name, reason):
    """
    Send email to village leader when a new visitor is registered.
    """
    subject = f"New Visitor Registered in {village_name}"
    message = (
        f"Dear Leader,\n\n"
        f"A new visitor has been registered in your village:\n"
        f"- Visitor: {visitor_name}\n"
        f"- Host: {host_name}\n"
        f"- Reason: {reason}\n\n"
        f"Village: {village_name}\n\n"
        f"Regards,\nSmart Village System"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [leader_email],
        fail_silently=False,
    )
