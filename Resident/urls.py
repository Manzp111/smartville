# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers


# Import your ViewSets
from .views import  ResidentViewSet
from .resident_views import ResidentByUserView,ResidentDetailView,ResidentsByVillageView

router = routers.DefaultRouter()
# router.register(r'locations', LocationViewSet)
# router.register(r'residents', ResidentViewSet)
router.register(r"resident", ResidentViewSet, basename="resident")


urlpatterns = [
    
    path('', include(router.urls)),
    path("residents/<uuid:resident_id>/", ResidentDetailView.as_view(), name="resident-detail"),
    path("residents/user/<uuid:user_id>/", ResidentByUserView.as_view(), name="resident-by-user"),
    path("village/<uuid:village_id>/residents/", ResidentsByVillageView.as_view(), name="residents-by-village"),

 
]