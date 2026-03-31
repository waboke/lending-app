from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class EligibilityDecisionStatus(models.TextChoices):
    ELIGIBLE = 'eligible', 'Eligible'
    NOT_ELIGIBLE = 'not_eligible', 'Not Eligible'
    REVIEW = 'review', 'Manual Review'


class CreditAssessment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_assessments')
    score = models.PositiveIntegerField(default=0)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    debt_to_income_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    decision = models.CharField(max_length=20, choices=EligibilityDecisionStatus.choices)
    reason = models.TextField(blank=True, null=True)
