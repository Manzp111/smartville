from django.urls import path
from .views import VillageNewsAPIView

urlpatterns = [
    path("village/<uuid:village_id>/news/", VillageNewsAPIView.as_view(), name="village-dashboard"),
]
