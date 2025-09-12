# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers


# Import your ViewSets
from .views import  ResidentViewSet

router = routers.DefaultRouter()
# router.register(r'locations', LocationViewSet)
# router.register(r'residents', ResidentViewSet)
router.register(r"resident", ResidentViewSet, basename="resident")

urlpatterns = [
    
    path('', include(router.urls)),

 
]