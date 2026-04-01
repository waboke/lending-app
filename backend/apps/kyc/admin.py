from django.contrib import admin
from .models import KYCSubmission


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'id_type', 'id_number', 'status', 'created_at')
    search_fields = ('user__email', 'id_number', 'branch__name')
    list_filter = ('status', 'branch', 'id_type')
