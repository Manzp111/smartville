from rest_framework.routers import DefaultRouter
from .views import VolunteeringEventViewSet,VillageEventViewSet
from django.urls import path,include

router = DefaultRouter()
router.register(r'volunteer/activity', VolunteeringEventViewSet, basename='event')




village_event_list = VillageEventViewSet.as_view({"get": "list"})

urlpatterns = [
    path("volunteer/<uuid:village_id>/actity", village_event_list, name="village-events"),
    path("",include(router.urls)),
]
