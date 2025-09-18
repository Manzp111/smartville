from rest_framework.routers import DefaultRouter
from .views import VolunteeringEventViewSet,VillageEventViewSet,VolunteerParticipationViewSet
from django.urls import path,include

router = DefaultRouter()
router.register(r'volunteer/activity', VolunteeringEventViewSet, basename='event_managment')
router.register(r'volunteer', VolunteeringEventViewSet, basename='voluntter')
router.register(r'volunteer/participations', VolunteerParticipationViewSet, basename='participation')




village_event_list = VillageEventViewSet.as_view({"get": "list"})

urlpatterns = [
    path("volunteer/<uuid:village_id>/actity", village_event_list, name="village-events"),
    path("",include(router.urls)),
    # path('villages/<str:village_id>/events/',VillageEventViewSet.as_view({'get': 'list'}),name='village-events'),
    
    # Additional endpoints for event approval
    path('volunteer/<uuid:pk>/approve/',VolunteeringEventViewSet.as_view({'post': 'approve'}),name='event-approve'),
    path('volunteer/<uuid:pk>/reject/',VolunteeringEventViewSet.as_view({'post': 'reject'}),name='event-reject'),
]
