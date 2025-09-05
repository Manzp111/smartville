from django.urls import path
from . import views
from .locationviews import LocatePointAPIView
urlpatterns = [
    path("locate/", views.locate_point, name="locate_village"),
    path("api/locate/", LocatePointAPIView.as_view(), name="locate_point_api"),
]
