import uuid
from django.db import models
from django.conf import settings
from Location.models import Location
from account.models import Person


class Visitor(models.Model):
    visitor_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    visitor_info = models.ForeignKey(Person, on_delete=models.CASCADE)
    host = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    visitor_location = models.ForeignKey(Location, on_delete=models.CASCADE)    
    reason_for_visit = models.TextField()   
    arrival_date = models.DateField(help_text="Date the visitor actually arrives")
    registered_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    departure_date = models.DateField(help_text="Date the visitor leaves", null=True, blank=True)

    def __str__(self):
        return f"Visitor {self.visitor_info} hosted by {self.host}"
