# volunteer/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VolunteeringEventViewSet, VillageEventViewSet
from .participation_viws import VolunteerParticipationViewSet

router = DefaultRouter()
router.register(r'volunter', VolunteeringEventViewSet, basename='volunteering-event')
router.register(r'participations', VolunteerParticipationViewSet, basename='participation')
urlpatterns = [
    path('', include(router.urls)),
   
    path("volunter/<uuid:village_id>/activity/",VillageEventViewSet.as_view({'get': 'list'}),name="village-events"
    ),
]
