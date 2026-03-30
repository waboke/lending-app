from django.conf import settings
from django.db import models
from apps.core.models import BaseModel
from apps.loan.models import Loan


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESSFUL = 'successful', 'Successful'
    FAILED = 'failed', 'Failed'


class PaymentTransaction(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=120, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)


class WebhookEvent(BaseModel):
    provider = models.CharField(max_length=50)
    event_id = models.CharField(max_length=120, unique=True)
    event_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
