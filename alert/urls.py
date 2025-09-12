from rest_framework.routers import DefaultRouter
from .views import CommunityAlertViewSet

router = DefaultRouter()
router.register(r'alerts', CommunityAlertViewSet, basename='alert')

urlpatterns = router.urls