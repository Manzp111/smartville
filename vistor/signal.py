from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Visitor

@receiver(post_save, sender=Visitor)
def notify_village_leader(sender, instance, created, **kwargs):
    """
    Sends an email to the village leader when a new visitor is created.
    """
    if created:  # Only when a new visitor is added
        village = instance.village
        if village and getattr(village, "leader", None):
            leader_email = getattr(village.leader, "email", None)
            if leader_email:
                try:
                    send_mail(
                        subject=f"New Visitor Added in {village.get_full_address()}",
                        message=f"{instance.resident.person.first_name} added a visitor: {instance.name}",
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                        recipient_list=[leader_email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"❌ Failed to send email to village leader: {e}")
