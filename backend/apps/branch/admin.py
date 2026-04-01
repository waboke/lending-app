from django.contrib import admin
from .models import Branch, BranchStaffAssignment


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'state', 'lga', 'phone_number', 'email', 'is_active')
    search_fields = ('name', 'code', 'state', 'lga')
    list_filter = ('state', 'is_active')


@admin.register(BranchStaffAssignment)
class BranchStaffAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'role', 'is_primary', 'is_active')
    search_fields = ('user__email', 'branch__name', 'role')
    list_filter = ('role', 'is_primary', 'is_active')
