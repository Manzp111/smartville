# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_village_leader_new_resident(leader_email, resident_name, village_name,location):
    subject = f"New Resident Joined Your Village ({village_name}located on {location})"
    message = f"{resident_name} has joined your village {village_name}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [leader_email])


@shared_task
def send_new_resident_email(leader_email, resident_name, village_name):
    subject = f"New Resident Added in {village_name}"
    message = f"A new resident, {resident_name}, has been added to your village."
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [leader_email],
        fail_silently=False,
    )

