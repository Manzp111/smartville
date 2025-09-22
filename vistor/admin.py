from django.contrib import admin
from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        "visitor_id",
        "name",
        "resident",
        "phone_number",
        "purpose_of_visit",
        "date",
        "time_in",
        "time_out",
        "village",
        "created_at",
    )
    list_filter = ("date", "village", "resident")
    search_fields = ("name", "phone_number", "id_number", "resident__name")
    ordering = ("-created_at",)
    readonly_fields = ("visitor_id", "created_at", "updated_at")
