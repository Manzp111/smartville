from django.urls import path
from . import views
from django.urls import path, include
from .locationviews import LocatePointAPIView,JoinVillageByCoordinatesAPIView
from rest_framework.routers import DefaultRouter
from .views import LocationViewSet,LeaderViewSet

router = DefaultRouter()
router.register(r'view/locations', LocationViewSet, basename='Village')
router.register(r'leaders', LeaderViewSet, basename='leader')


urlpatterns = [
    path("locate/", views.locate_point, name="locate_village"),
    path("locate/place/", LocatePointAPIView.as_view(), name="locate_point_api"),
    path('',include(router.urls)),
    path('join-community-by-coordinates/', JoinVillageByCoordinatesAPIView.as_view(), name='join-by-coordinates'),
  
]
