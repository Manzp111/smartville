# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_village_leader_new_resident(leader_email, resident_name, village_name):
    subject = f"New Resident Joined Your Village ({village_name})"
    message = f"{resident_name} has joined your village {village_name}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [leader_email])
