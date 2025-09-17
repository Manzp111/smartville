from django.contrib import admin
from django import forms
from django.forms import TimeInput
from .models import Event


# Custom form to use time picker for start_time and end_time
class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "start_time": TimeInput(attrs={"type": "time"}),
            "end_time": TimeInput(attrs={"type": "time"}),
        }


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm

    # Columns to show in the list view
    list_display = (
        "event_id",
        "title",
        "organizer",
        "date",
        "village",
        "start_time",
        "end_time",
        "status",
        "created_at",
    )

    # Filters on sidebar
    list_filter = ("status", "date", "organizer")

    # Search fields
    search_fields = ("title", "description", "Village", "organizer__email")

    # Default ordering
    ordering = ("-created_at",)

    # Fields not editable
    readonly_fields = ("event_id", "created_at", "updated_at")

    # Custom admin actions
    actions = ["approve_events", "reject_events", "cancel_events"]

    # Action methods
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
