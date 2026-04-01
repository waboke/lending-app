from django.contrib import admin
from .models import Profile, BankAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'home_branch', 'customer_category', 'residency_status', 'country_of_residence', 'state_of_residence')
    search_fields = ('user__email', 'first_name', 'last_name', 'bvn', 'nin')
    list_filter = ('customer_category', 'residency_status', 'country_of_residence', 'state_of_residence', 'home_branch')


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'account_name', 'account_number', 'is_default')
    search_fields = ('user__email', 'bank_name', 'account_number')
