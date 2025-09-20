import uuid
from django.db import models
from account.models import Person
from django.conf import settings
from Village.models import Village

ALERT_STATUS_CHOICES = [
    ("PENDING", "Pending Review"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("RESOLVED", "Resolved"),
]

ALERT_TYPE_CHOICES = [
    ('emergency', 'Emergency'),
    ('security', 'Security'),
    ('infrastructure', 'Infrastructure'),
    ('health', 'Health'),
    ('environment', 'Environmental'),
    ('utility', 'Utility Problem'),
    ('social', 'Social Issue')
]

URGENCY_LEVEL_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical')
]

class CommunityAlert(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    urgency_level = models.CharField(max_length=30, choices=URGENCY_LEVEL_CHOICES)
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default="PENDING")
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reported_alerts"
    )
    village = models.ForeignKey(Village, on_delete=models.CASCADE, related_name='alerts')
    specific_location = models.CharField(max_length=100, blank=True, null=True)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    allow_sharing = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.village})"