from django.conf import settings
from django.db import models
from apps.core.models import BaseModel


class Branch(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=100)
    lga = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class BranchStaffRole(models.TextChoices):
    BRANCH_MANAGER = 'branch_manager', 'Branch Manager'
    LOAN_OFFICER = 'loan_officer', 'Loan Officer'
    CREDIT_OFFICER = 'credit_officer', 'Credit Officer'
    KYC_OFFICER = 'kyc_officer', 'KYC Officer'
    CASHIER = 'cashier', 'Cashier'
    SUPPORT = 'support', 'Support'


class BranchStaffAssignment(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='branch_assignments')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='staff_assignments')
    role = models.CharField(max_length=50, choices=BranchStaffRole.choices)
    is_primary = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'branch', 'role')
        ordering = ['branch__name', 'role']

    def __str__(self):
        return f'{self.user.email} - {self.branch.name} - {self.role}'
