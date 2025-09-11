from django.urls import path
from . import views
from django.urls import path, include
from .locationviews import LocatePointAPIView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()


urlpatterns = [
    path("locate/", views.locate_point, name="locate_village"),
    # path("api/locate/", LocatePointAPIView.as_view(), name="locate_point_api"),
  
]
