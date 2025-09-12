from django.urls import path
from . import views
from django.urls import path, include
from .locationviews import LocatePointAPIView
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet

router = DefaultRouter()
router.register(r'view/locations', LocationViewSet, basename='location')


urlpatterns = [
    path("locate/", views.locate_point, name="locate_village"),
    path("locate/place/", LocatePointAPIView.as_view(), name="locate_point_api"),
    path('',include(router.urls)),
  
]
