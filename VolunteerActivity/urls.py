from rest_framework.routers import DefaultRouter
from .views import VolunteeringEventViewSet

router = DefaultRouter()
router.register(r'volunteer/activity', VolunteeringEventViewSet, basename='event')

urlpatterns = router.urls
