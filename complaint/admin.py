
from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'complainant', 'location', 'status', 'date_submitted', 'is_anonymous')
    list_filter = ('status', 'is_anonymous', 'location')
    search_fields = ('description', 'complainant__first_name', 'complainant__last_name')
    ordering = ('-date_submitted',)
