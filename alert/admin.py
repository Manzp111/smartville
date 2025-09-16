from django.contrib import admin
from .models import CommunityAlert

@admin.register(CommunityAlert)
class CommunityAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'alert_type', 'urgency_level', 'status', 'village', 'incident_date', 'created_at')
    search_fields = ('title', 'description', 'alert_type', 'village__village')
    list_filter = ('status', 'urgency_level', 'alert_type', 'village')