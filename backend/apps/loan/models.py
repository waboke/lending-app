from django.conf import settings
from django.db import models
from apps.core.models import BaseModel
from apps.user_profile.models import CustomerCategory
from apps.branch.models import Branch


class LoanApplicationStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    IN_REVIEW = 'in_review', 'In Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class BranchDecisionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    RECOMMENDED = 'recommended', 'Recommended'
    NOT_RECOMMENDED = 'not_recommended', 'Not Recommended'


class LoanStatus(models.TextChoices):
    PENDING_DISBURSEMENT = 'pending_disbursement', 'Pending Disbursement'
    ACTIVE = 'active', 'Active'
    OVERDUE = 'overdue', 'Overdue'
    CLOSED = 'closed', 'Closed'


class LoanProduct(BaseModel):
    name = models.CharField(max_length=150)
    customer_category = models.CharField(max_length=30, choices=CustomerCategory.choices, null=True, blank=True)
    is_diaspora_allowed = models.BooleanField(default=False)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class LoanApplication(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loan_applications')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='loan_applications')
    product = models.ForeignKey(LoanProduct, on_delete=models.CASCADE)
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_months = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=LoanApplicationStatus.choices, default=LoanApplicationStatus.DRAFT)
    branch_decision = models.CharField(max_length=30, choices=BranchDecisionStatus.choices, default=BranchDecisionStatus.PENDING)
    branch_decision_note = models.TextField(blank=True, null=True)
    review_note = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_loan_applications')


class Loan(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='loans')
    application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='loan')
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tenure_months = models.PositiveIntegerField()
    total_repayment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding_balance = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30, choices=LoanStatus.choices, default=LoanStatus.PENDING_DISBURSEMENT)
    disbursed_at = models.DateTimeField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)


class RepaymentSchedule(BaseModel):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayment_schedules')
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['installment_number']
