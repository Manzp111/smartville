from django.db import models
from account.models import Person
from Location.models import Location

import uuid

# Create your models here.

class Complaint(models.Model):
    complaint_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    complainant = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='complaints')
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='complaints')
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('resolved', 'Resolved')], default='pending')
