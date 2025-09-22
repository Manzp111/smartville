from django.contrib import admin
from django.urls import path,include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
     path('', TemplateView.as_view(template_name='home/home.html'), name='home'),
    path('',include('account.urls')),

    path('api/event/',include('event.urls')),
    path('api/complaint/', include('complaint.urls')),
    path('api/alert/', include('alert.urls')),

    path('',include('event.urls')),
    path('',include('Village.urls')),
    path('',include("Resident.urls")),
    path('',include('villagesInfo.urls')),
    path("",include("VolunteerActivity.urls")),
    path("",include("team_contact.urls")),
    path('',include("vistor.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
