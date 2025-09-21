import uuid
from django.db import models
from account.models import Person
from django.conf import settings
from Village.models import Village


STATUS_CHOICES = [
    ("PENDING", "Pending Approval"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("CANCELLED", "Cancelled"),
]

CATEGORY_CHOICES = [
    # 1. Community Engagement / Social Events
    ("Village Meeting", "Village Meeting"),
    ("Festival & Celebration", "Festival & Celebration"),
    ("Workshop / Seminar", "Workshop / Seminar"),  

    # 2. Health & Wellness
    ("Health Screening", "Health Screening"),
    ("Fitness Event", "Fitness Event"),
    ("Nutrition & Hygiene Campaign", "Nutrition & Hygiene Campaign"),

    # 3. Educational / Training
    ("School Event", "School Event"),
    ("Adult Education Program", "Adult Education Program"),
    ("Tech / Digital Training", "Tech / Digital Training"),

    # 4. Emergency / Safety
    ("Disaster Preparedness Drill", "Disaster Preparedness Drill"),
    ("Community Policing Event", "Community Policing Event"),
    ("Incident Reporting Workshop", "Incident Reporting Workshop"),

    # 5. Environmental / Infrastructure
    ("Village Development Project", "Village Development Project"),
    ("Cleanliness Drive", "Cleanliness Drive"),
    ("Sustainable Agriculture", "Sustainable Agriculture"),

    # 6. Economic / Livelihood
    ("Market Day / Fair", "Market Day / Fair"),
    ("Entrepreneurship Workshop", "Entrepreneurship Workshop"),
    ("Job / Skills Fair", "Job / Skills Fair"),

    # 7. Special / One-off Events
    ("Visit by Dignitary", "Visit by Dignitary"),
    ("Competition / Award", "Competition / Award"),
    ("Emergency Relief Distribution", "Emergency Relief Distribution"),
]

TYPE_CHOICES = [
    ("Announcement", "Announcement"),
    ("Alert", "Alert"),
    ("Emergency", "Emergency"),
    ("Reminder", "Reminder"),
    ("Update", "Update"),
    ("Invitation", "Invitation"),
]


class Event(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    exact_place_of_village = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,default="Village Meeting")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,default="Announcement")

    image = models.ImageField(upload_to="events/images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE)

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
