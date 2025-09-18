from django.contrib import admin
from .models import TeamMember, ContactMessage, ContactReply

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'created_at')
    search_fields = ('name', 'role', 'email')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'inquiry_type', 'status', 'message', 'created_at')
    search_fields = ('name', 'email', 'organization', 'message')
    list_filter = ('status', 'inquiry_type')

@admin.register(ContactReply)
class ContactReplyAdmin(admin.ModelAdmin):
    list_display = ('message', 'replied_by', 'replied_at')
    search_fields = ('reply_message',)