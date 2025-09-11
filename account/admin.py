from django.contrib import admin
from .models import User, Person, OTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active', 'is_staff', 'is_superuser','is_verified')
    search_fields = ('email',)
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser','is_verified')
    ordering = ('email',)
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone_number')
    search_fields = ('first_name', 'last_name', 'phone_number')
    # list_filter = ('location',)
    ordering = ('first_name',)

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'purpose', 'created_at', 'is_used')
    search_fields = ('user__email', 'code', 'purpose')
    list_filter = ('purpose', 'is_used', 'created_at')
    ordering = ('-created_at',)