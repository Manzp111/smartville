from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id","village","cell", "sector", "district", "province", "leader")
    search_fields = ("village", "sector", "district", "province", "leader__email")
    list_filter = ("province", "district", "sector","cell")
    ordering = ("id","province", "district", "sector", "cell", "village")
