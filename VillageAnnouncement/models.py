# from django.db import models
# from django.contrib.auth.models import User
# from Location.models import Location
# import uuid

# class VolunteeringEvent(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     date = models.DateField()
#     location = models.CharField(max_length=200)
#     capacity = models.PositiveIntegerField()  # max volunteers
#     volunteers = models.ManyToManyField(User, blank=True, related_name="volunteering_events")
#     village=models.ForeignKey(Location,on_delete=models.CASCADE)

#     @property
#     def current_volunteers(self):
#         return self.volunteers.count()

#     @property
#     def is_full(self):
#         return self.current_volunteers >= self.capacity

#     def __str__(self):
#         return self.title
