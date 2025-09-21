from django.contrib import admin
from .models import Resident

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('resident_id', 'person', 'village__village',  'added_by', 'status', 'created_at', 'updated_at')
    search_fields = ('person__first_name', 'person__last_name', 'village__village', 'village__cell', 'village__sector')
    list_filter = ('has_account', 'is_deleted', 'village__province', 'village__district', 'village__sector')
    ordering = ('village__province', 'village__district', 'village__sector', 'person__first_name')

    actions = ['soft_delete_residents', 'restore_residents']

   
    def soft_delete_residents(self, request, queryset):
        for resident in queryset:
            resident.soft_delete()
    soft_delete_residents.short_description = "Soft delete selected residents"

    
    def restore_residents(self, request, queryset):
        for resident in queryset:
            resident.restore()
    restore_residents.short_description = "Restore selected residents"
