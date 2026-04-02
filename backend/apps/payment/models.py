from django.conf import settings
from django.db import models
from apps.core.models import BaseModel
from apps.loan.models import Loan
from apps.user_profile.models import BankAccount


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESSFUL = 'successful', 'Successful'
    FAILED = 'failed', 'Failed'


class AutoDebit(models.TextChoices):
    ENABLED = 'enabled', 'Enabled'
    DISABLED = 'disabled', 'Disabled'
    SUSPENDED = 'suspended', 'Suspended'


class AutoDebitSetup(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auto_debit_setup')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='auto_debit_setups')
    status = models.CharField(max_length=20, choices=AutoDebit.choices, default=AutoDebit.DISABLED)
    max_amount_per_debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    frequency = models.CharField(max_length=20, default='monthly')  # monthly, weekly, etc.
    next_debit_date = models.DateField(null=True, blank=True)

    class Meta:
        app_label = 'payment'


class PaymentTransaction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=120, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'payment'


class WebhookEvent(BaseModel):
    provider = models.CharField(max_length=50)
    event_id = models.CharField(max_length=120, unique=True)
    event_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)

    class Meta:
        app_label = 'payment'
