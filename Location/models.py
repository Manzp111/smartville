from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    sector = models.CharField(max_length=50)
    cell = models.CharField(max_length=50)
    village = models.CharField(max_length=50)
    leader = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='led_villages')

    def __str__(self):
        return f"{self.id}-{self.village},{self.cell}, {self.sector}, {self.district}, {self.province}"
