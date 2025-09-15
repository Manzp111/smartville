from django.db import models
from django.conf import settings
import uuid



class Location(models.Model):
    village_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # use string reference
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='led_villages'
    )

    def __str__(self):
        return f"{self.id}-{self.village},{self.cell}, {self.sector}, {self.district}, {self.province}"
