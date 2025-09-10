from django.db import models
from account.models import Person
from Location.models import Location
import uuid

class Resident(models.Model):
    resident_id=models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person_id=models.ForeignKey(Person,on_delete=models.CASCADE)
    village_id=models.ForeignKey(Location,on_delete=models.CASCADE)
