from django.contrib import admin
from .models import VolunteeringEvent, VolunteerParticipation


class VolunteerParticipationInline(admin.TabularInline):
    model = VolunteerParticipation
    extra = 0
    readonly_fields = ("user", "joined_at", "status")
    can_delete = False


@admin.register(VolunteeringEvent)
class VolunteeringEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "village",
        "date",
        "capacity",
        "approved_volunteers_count",
        "is_full",
        "organizer",
    )
    list_filter = ("date", "village", "organizer")
    search_fields = ("title", "description", "village__name", "organizer__phone_number")
    inlines = [VolunteerParticipationInline]

    fieldsets = (
        ("Event Details", {
            "fields": ("title", "description", "date", "capacity")
        }),
        ("Organizer & Location", {
            "fields": ("village", "organizer")
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Prevent editing after creation if needed
            return ("approved_volunteers_count", "is_full")
        return ()


@admin.action(description="Approve selected participations")
def approve_participations(modeladmin, request, queryset):
    queryset.update(status="APPROVED")


@admin.action(description="Reject selected participations")
def reject_participations(modeladmin, request, queryset):
    queryset.update(status="REJECTED")


@admin.register(VolunteerParticipation)
class VolunteerParticipationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "joined_at")
    list_filter = ("status", "event__date", "event__village")
    search_fields = ("user__phone_number", "event__title")
    readonly_fields = ("joined_at",)
    actions = [approve_participations, reject_participations]

    fieldsets = (
        (None, {
            "fields": ("user", "event", "status")
        }),
        ("Meta", {
            "fields": ("joined_at",)
        }),
    )
