from rest_framework.routers import DefaultRouter
from .views import EventViewSet
from django.urls import path,include
router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')




from .views import EventsByVillageAPIView

urlpatterns = [
     path("/event/village/<uuid:village_id>/events/", EventsByVillageAPIView.as_view(), name="village-events"),
    path("",include(router.urls)),

]

