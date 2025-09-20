from django.core.mail import send_mail
from django.conf import settings
from django.db import models
import uuid
from django.utils import timezone
from rest_framework.exceptions import ValidationError


class Visitor(models.Model):
    visitor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resident = models.ForeignKey(
        'Resident.Resident',  # Update with correct Resident model import
        on_delete=models.CASCADE,
        related_name="visitors"
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50)
    purpose_of_visit = models.TextField()
    expected_duration = models.CharField(max_length=50)
    vehicle_info = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    time_in = models.TimeField(default=timezone.now)
    time_out = models.TimeField(null=True, blank=True)
    village = models.ForeignKey(
        'Village.Village',
        on_delete=models.CASCADE,
        related_name="visitors",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.resident.status != "APPROVED":
            raise ValidationError("Resident is not approved")
        super().save(*args, **kwargs)

