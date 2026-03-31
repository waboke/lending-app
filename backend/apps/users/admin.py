from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'phone_number', 'role', 'is_staff', 'is_phone_verified', 'is_email_verified')
    search_fields = ('email', 'phone_number')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_phone_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'phone_number', 'role')}),
        ('Verification', {'fields': ('is_phone_verified', 'is_email_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )
