from django.contrib import admin
from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "visitor_id",
        "visitor_info",
        "host",
        "visitor_location",
        "reason_for_visit",
        "arrival_date",
        "departure_date",
        "registered_date",
        "updated_at",
    )
    list_filter = ("arrival_date", "departure_date", "visitor_location", "host")
    search_fields = ("visitor_info__first_name", "visitor_info__last_name", "host__email", "reason_for_visit")
    ordering = ("-registered_date",)
    actions = ["delete_selected"]  # default bulk delete action

    # Optional: customize display for visitor info
    def visitor_info(self, obj):
        return f"{obj.visitor_info.first_name} {obj.visitor_info.last_name}"

    visitor_info.short_description = "Visitor Name"
