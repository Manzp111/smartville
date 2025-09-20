from django.contrib import admin
from .models import VolunteeringEvent, VolunteerParticipation
from django.utils import timezone
class VolunteerParticipationInline(admin.TabularInline):
    model = VolunteerParticipation
    extra = 0
    readonly_fields = (  "user", "status", "joined_at", "updated_at", "approved_at")
    can_delete = False


@admin.register(VolunteeringEvent)
class VolunteeringEventAdmin(admin.ModelAdmin):
    list_display = (
        "volunteer_id",
        "title", "village", "organizer", "status",
        "date", "capacity", "approved_volunteers_count",
        "is_full", "available_spots"
    )
    list_filter = ("status", "village", "date")
    search_fields = ("title", "description", "organizer__username", "village__village")
    ordering = ("-date",)
    inlines = [VolunteerParticipationInline]

    readonly_fields = ("approved_volunteers_count", "is_full", "available_spots", "created_at", "updated_at", "approved_at")


@admin.register(VolunteerParticipation)
class VolunteerParticipationAdmin(admin.ModelAdmin):
    list_display = ( "participation_id", "user", "event", "status", "joined_at", "updated_at", "approved_at")
    list_filter = ("status", "joined_at", "event__village", "event__date")
    search_fields = ("user__username", "event__title", "event__village__village")
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at", "updated_at", "approved_at")

    # Custom admin actions
    actions = ["approve_participation", "reject_participation"]

    def approve_participation(self, request, queryset):
        updated = queryset.update(status="approved", approved_at=timezone.now())
        self.message_user(request, f"{updated} participation(s) approved successfully.")
    approve_participation.short_description = "Approve selected participations"

    def reject_participation(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} participation(s) rejected successfully.")
    reject_participation.short_description = "Reject selected participations"
