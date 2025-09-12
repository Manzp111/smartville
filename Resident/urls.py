# project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers


# Import your ViewSets
from .views import LocationViewSet, ResidentViewSet

router = routers.DefaultRouter()
router.register(r'locations', LocationViewSet)
router.register(r'residents', ResidentViewSet)

urlpatterns = [
    
    path('resident/', include(router.urls)),

 
]