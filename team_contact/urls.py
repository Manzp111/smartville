from rest_framework.routers import DefaultRouter
from .views import TeamMemberViewSet, ContactMessageViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'team/contact', TeamMemberViewSet, basename='team')
router.register(r'contact', ContactMessageViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]