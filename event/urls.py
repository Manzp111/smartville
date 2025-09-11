from rest_framework.routers import DefaultRouter
from event.views import EventViewSet, EventAttendanceViewSet

router = DefaultRouter()
router.register(r'attendance', EventAttendanceViewSet)
router.register(r'events', EventViewSet, basename='event')

urlpatterns = router.urls