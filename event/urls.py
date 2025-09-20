from rest_framework.routers import DefaultRouter
from .views import EventViewSet,EventViewSetlist
from django.urls import path,include
router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')

village_event_list = EventViewSetlist.as_view({"get": "list"})



from .views import EventsByVillageAPIView

urlpatterns = [
    path("village/<uuid:village_id>/events/", EventsByVillageAPIView.as_view(), name="village-events"),
    path("",include(router.urls)),
    path("event/<uuid:village_id>/village", village_event_list, name="village-events"),

    

]

