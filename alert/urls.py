from rest_framework.routers import DefaultRouter
from .views import CommunityAlertViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'alerts', CommunityAlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls))
]