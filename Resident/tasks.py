# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_village_leader_new_resident(leader_email, resident_name, village_name,Village):
    subject = f"New Resident Joined Your Village ({village_name}located on {Village})"
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
# tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def notify_village_leaders_of_migration(resident_name, old_location_id, new_location_id):
    """
    Notify old and new village leaders about a resident migration.

    Args:
        resident_name (str): Full name of the resident.
        old_location_id (str/UUID): ID of the old Village.
        new_location_id (str/UUID): ID of the new Village.
    """
    from Resident.models import Village  # Import here to avoid circular import

    old_location = Village.objects.filter(village_id=old_location_id).first()
    new_location = Village.objects.filter(village_id=new_location_id).first()

    # Notify old leader if exists
    if old_location and old_location.leader and old_location.leader.email:
        send_mail(
            subject=f"Resident {resident_name} moved from your village",
            message=(
                f"Dear Leader,\n\n"
                f"The resident {resident_name} has migrated from your village '{old_location.village}'.\n"
                f"Please take note.\n\nThank you."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[old_location.leader.email],
            fail_silently=False
        )

    # Notify new leader if exists
    if new_location and new_location.leader and new_location.leader.email:
        send_mail(
            subject=f"New resident in your village '{new_location.village}'",
            message=(
                f"Dear Leader,\n\n"
                f"The resident {resident_name} has been moved to your village '{new_location.village}' by the admin.\n"
                f"Please review and approve if necessary.\n\nThank you."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_location.leader.email],
            fail_silently=False
        )

    return f"Notifications sent for {resident_name}"
