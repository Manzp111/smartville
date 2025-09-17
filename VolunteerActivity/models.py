# event/models.py
from django.db import models
from account.models import User
from Village.models import Village
import uuid

class VolunteeringEvent(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    capacity = models.PositiveIntegerField()
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_organizer")

    @property
    def approved_volunteers_count(self):
        return self.volunteerparticipation_set.filter(status='APPROVED').count()

    @property
    def is_full(self):
        return self.approved_volunteers_count >= self.capacity

    def __str__(self):
        return self.title


class VolunteerParticipation(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending Approval"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(VolunteeringEvent, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user} - {self.event} ({self.status})"
