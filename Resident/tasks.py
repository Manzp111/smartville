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
# account/tasks.py
# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_village_leaders_of_migration(resident_name, old_village, old_leader_email, new_village, new_leader_email):
    """
    Notify both old and new village leaders about a resident migration.

    Args:
        resident_name (str): Full name of the resident.
        old_village (str): Name of the old village (can be None if no old record).
        old_leader_email (str): Email of the old village leader (can be None).
        new_village (str): Name of the new village.
        new_leader_email (str): Email of the new village leader (can be None).
    """

    # Notify old village leader if email is provided
    if old_leader_email and old_village:
        send_mail(
            subject=f"Resident {resident_name} moved from your village",
            message=(
                f"Dear Leader,\n\n"
                f"The resident {resident_name} has migrated from your village '{old_village}'.\n"
                f"Please take note.\n\nThank you."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[old_leader_email],
            fail_silently=False
        )

    # Notify new village leader if email is provided
    if new_leader_email and new_village:
        send_mail(
            subject=f"New resident in your village '{new_village}'",
            message=(
                f"Dear Leader,\n\n"
                f"The resident {resident_name} has been moved to your village '{new_village}' by the admin.\n"
                f"Please review and approve if necessary.\n\nThank you."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_leader_email],
            fail_silently=False
        )

    return f"Notifications sent for {resident_name}"
