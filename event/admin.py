from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "organizer",
        "date",
        "start_time",
        "end_time",
        "image",
        "status",
        "created_at",

    )
    list_filter = ("status", "date", "organizer")
    search_fields = ("title", "description", "location", "organizer__email")
    ordering = ("-created_at",)

    # Show event_id but not editable
    readonly_fields = ("event_id", "created_at", "updated_at")

    # Custom actions
    actions = ["approve_events", "reject_events", "cancel_events"]

    def approve_events(self, request, queryset):
        updated = queryset.update(status="APPROVED")
        self.message_user(request, f"{updated} event(s) successfully approved.")
    approve_events.short_description = "Approve selected events"

    def reject_events(self, request, queryset):
        updated = queryset.update(status="REJECTED")
        self.message_user(request, f"{updated} event(s) rejected.")
    reject_events.short_description = "Reject selected events"

    def cancel_events(self, request, queryset):
        updated = queryset.update(status="CANCELLED")
        self.message_user(request, f"{updated} event(s) cancelled.")
    cancel_events.short_description = "Cancel selected events"
