import uuid

from django.db import models
from account.models import Person
from django.conf import settings
from Location.models import Location


STATUS_CHOICES = [
    ("PENDING", "Pending Approval"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("CANCELLED", "Cancelled"),
]

class Event(models.Model):

    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    image = models.ImageField(upload_to="events/images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    village = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='events')

    def __str__(self):
        return f"{self.title} ({self.date})"
    

class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='events_joined')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event','person')

        def __str__(self):
            return f"{self.person} joined {self.event}"
