from django.db import models
from account.models import Person
from Location.models import Location

import uuid

class CommunityAlert(models.Model):
    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='alerts')
    title = models.CharField(max_length=100)
    description = models.TextField()
    alert_type = models.CharField(max_length=30)
    urgency_level = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('closed', 'Closed')], default='active')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='alerts')
    specific_location = models.CharField(max_length=100, blank=True, null=True)
    incident_date = models.DateField()
    incident_time = models.TimeField()
    allow_sharing = models.BooleanField(default=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)