from django.db import models
from account.models import Person
from Location.models import Location
import uuid

class Resident(models.Model):
    resident_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="residencies")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="residents")

    def __str__(self):
        return f"{self.person} @ {self.location.village}"

