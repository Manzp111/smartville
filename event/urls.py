from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from event.views import EventViewSet, EventAttendanceViewSet

router = DefaultRouter()
router.register(r'attendance', EventAttendanceViewSet)
router.register(r'events', EventViewSet, basename='event')
=======
from .views import EventViewSet
from django.urls import path,include
router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')




from .views import EventsByVillageAPIView

urlpatterns = [
     path("village/<uuid:village_id>/events/", EventsByVillageAPIView.as_view(), name="village-events"),
    path("",include(router.urls)),

]
>>>>>>> main

