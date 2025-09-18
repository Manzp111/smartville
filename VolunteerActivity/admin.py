from django.contrib import admin
from .models import VolunteeringEvent, VolunteerParticipation


class VolunteerParticipationInline(admin.TabularInline):
    model = VolunteerParticipation
    extra = 0
    readonly_fields = ("user", "status", "joined_at", "updated_at")
    can_delete = False


@admin.register(VolunteeringEvent)
class VolunteeringEventAdmin(admin.ModelAdmin):
    list_display = (
        "title", "village", "organizer", "status",
        "date", "capacity", "approved_volunteers_count",
        "is_full", "available_spots"
    )
    list_filter = ("status", "village", "date")
    search_fields = ("title", "description", "organizer__username", "village__name")
    ordering = ("-date",)
    inlines = [VolunteerParticipationInline]

    fieldsets = (
        ("Event Details", {
            "fields": ("title", "description", "date", "village", "organizer")
        }),
        ("Capacity & Approval", {
            "fields": ("capacity", "status", "rejection_reason")
        }),
        ("System Info", {
            "fields": ("approved_volunteers_count", "is_full", "available_spots"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("approved_volunteers_count", "is_full", "available_spots", "created_at", "updated_at")


@admin.register(VolunteerParticipation)
class VolunteerParticipationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "joined_at", "updated_at")
    list_filter = ("status", "joined_at", "event__village", "event__date")
    search_fields = ("user__username", "event__title", "event__village__name")
    ordering = ("-joined_at",)
