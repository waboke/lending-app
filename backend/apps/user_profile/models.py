from django.conf import settings
from django.db import models
from apps.core.models import BaseModel
from apps.branch.models import Branch


class CustomerCategory(models.TextChoices):
    MILITARY = 'military', 'Military'
    PARAMILITARY = 'paramilitary', 'Paramilitary'
    CIVIL_SERVANT = 'civil_servant', 'Civil Servant'
    PRIVATE_SECTOR = 'private_sector', 'Private Sector'
    BUSINESSMAN = 'businessman', 'Businessman'


class ResidencyStatus(models.TextChoices):
    RESIDENT_NIGERIA = 'resident_nigeria', 'Resident Nigeria'
    DIASPORA = 'diaspora', 'Diaspora'


class CurrencyPreference(models.TextChoices):
    NGN = 'NGN', 'Naira'
    USD = 'USD', 'US Dollar'
    GBP = 'GBP', 'Pound'
    EUR = 'EUR', 'Euro'


class VerificationStatus(models.TextChoices):
    NOT_VERIFIED = 'not_verified', 'Not Verified'
    PENDING = 'pending', 'Pending'
    VERIFIED = 'verified', 'Verified'
    FAILED = 'failed', 'Failed'


class Profile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    home_branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profiles')
    customer_category = models.CharField(max_length=30, choices=CustomerCategory.choices)
    residency_status = models.CharField(max_length=30, choices=ResidencyStatus.choices)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    national_id = models.CharField(max_length=50, blank=True, null=True)
    bvn = models.CharField(max_length=20, blank=True, null=True)
    nin = models.CharField(max_length=20, blank=True, null=True)
    bvn_verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.NOT_VERIFIED)
    nin_verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.NOT_VERIFIED)
    country_of_residence = models.CharField(max_length=100, default='Nigeria')
    state_of_residence = models.CharField(max_length=100, blank=True, null=True)
    foreign_address = models.TextField(blank=True, null=True)
    has_nigerian_bank_account = models.BooleanField(default=True)
    has_foreign_bank_account = models.BooleanField(default=False)
    currency_preference = models.CharField(max_length=10, choices=CurrencyPreference.choices, default=CurrencyPreference.NGN)
    employer_name = models.CharField(max_length=255, blank=True, null=True)
    staff_or_service_number = models.CharField(max_length=100, blank=True, null=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    business_name = models.CharField(max_length=255, blank=True, null=True)
    average_monthly_turnover = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    years_in_business = models.PositiveIntegerField(default=0)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        app_label = 'user_profile'

    def is_salaried(self):
        return self.customer_category in [
            CustomerCategory.MILITARY,
            CustomerCategory.PARAMILITARY,
            CustomerCategory.CIVIL_SERVANT,
            CustomerCategory.PRIVATE_SECTOR,
        ]

    def risk_bucket(self):
        if self.residency_status == ResidencyStatus.RESIDENT_NIGERIA:
            return 'SALARIED_LOCAL' if self.is_salaried() else 'BUSINESS_LOCAL'
        return 'SALARIED_DIASPORA' if self.is_salaried() else 'BUSINESS_DIASPORA'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class BankAccount(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=120)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=10, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    is_salary_account = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_reference = models.CharField(max_length=120, blank=True, null=True)
