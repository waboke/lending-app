from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.credit.models import CreditAssessment, EligibilityDecisionStatus
from apps.kyc.models import KYCStatus
from .models import (
    LoanProduct,
    LoanApplication,
    Loan,
    RepaymentSchedule,
    LoanApplicationStatus,
    LoanStatus,
    BranchDecisionStatus,
)


def get_available_products(user):
    profile = user.profile
    qs = LoanProduct.objects.filter(is_active=True).filter(
        models.Q(customer_category__isnull=True) | models.Q(customer_category=profile.customer_category)
    )
    if profile.residency_status == 'diaspora':
        qs = qs.filter(is_diaspora_allowed=True)
    return qs


def validate_borrower_for_application(user, product, requested_amount):
    if not getattr(user, 'is_phone_verified', False):
        raise ValueError('Phone must be verified before applying')
    if not hasattr(user, 'profile'):
        raise ValueError('Profile is required')
    if not user.profile.home_branch:
        raise ValueError('A Nigerian home branch must be selected before applying')
    if not hasattr(user, 'kyc_submission') or user.kyc_submission.status != KYCStatus.APPROVED:
        raise ValueError('KYC must be approved before applying')
    assessment = CreditAssessment.objects.filter(user=user).order_by('-created_at').first()
    if not assessment or assessment.decision not in [EligibilityDecisionStatus.ELIGIBLE, EligibilityDecisionStatus.REVIEW]:
        raise ValueError('Run credit assessment first')
    if requested_amount > assessment.max_loan_amount:
        raise ValueError('Requested amount exceeds eligibility limit')
    active_exists = Loan.objects.filter(user=user, status__in=[LoanStatus.PENDING_DISBURSEMENT, LoanStatus.ACTIVE, LoanStatus.OVERDUE]).exists()
    if active_exists:
        raise ValueError('Only one active loan is allowed in MVP')
    if requested_amount < product.min_amount or requested_amount > product.max_amount:
        raise ValueError('Amount outside product limits')


@transaction.atomic
def submit_application(application: LoanApplication):
    validate_borrower_for_application(application.user, application.product, application.requested_amount)
    application.branch = application.user.profile.home_branch
    application.status = LoanApplicationStatus.SUBMITTED
    application.save(update_fields=['branch', 'status', 'updated_at'])
    return application


@transaction.atomic
def recommend_application(application: LoanApplication, reviewer, recommended: bool, note: str = ''):
    if application.status not in [LoanApplicationStatus.SUBMITTED, LoanApplicationStatus.IN_REVIEW]:
        raise ValueError('Only submitted or in review applications can be recommended')
    application.status = LoanApplicationStatus.IN_REVIEW
    application.branch_decision = BranchDecisionStatus.RECOMMENDED if recommended else BranchDecisionStatus.NOT_RECOMMENDED
    application.branch_decision_note = note
    application.reviewed_by = reviewer
    application.save(update_fields=['status', 'branch_decision', 'branch_decision_note', 'reviewed_by', 'updated_at'])
    return application


@transaction.atomic
def approve_application(application: LoanApplication, reviewer=None):
    if application.status not in [LoanApplicationStatus.SUBMITTED, LoanApplicationStatus.IN_REVIEW]:
        raise ValueError('Only submitted or in review applications can be approved')
    application.status = LoanApplicationStatus.APPROVED
    if reviewer:
        application.reviewed_by = reviewer
    application.save(update_fields=['status', 'reviewed_by', 'updated_at'])
    principal = application.requested_amount
    rate = application.product.interest_rate
    total_interest = principal * (rate / Decimal('100'))
    total_repayment = principal + total_interest
    loan = Loan.objects.create(
        user=application.user,
        branch=application.branch,
        application=application,
        principal=principal,
        interest_rate=rate,
        tenure_months=application.tenure_months,
        total_repayment_amount=total_repayment,
        outstanding_balance=total_repayment,
        status=LoanStatus.PENDING_DISBURSEMENT,
    )
    return loan


@transaction.atomic
def disburse_loan(loan: Loan):
    if loan.status != LoanStatus.PENDING_DISBURSEMENT:
        raise ValueError('Loan cannot be disbursed in current state')
    loan.status = LoanStatus.ACTIVE
    loan.disbursed_at = timezone.now()
    loan.due_date = (timezone.now() + relativedelta(months=loan.tenure_months)).date()
    loan.save(update_fields=['status', 'disbursed_at', 'due_date', 'updated_at'])
    installment_total = loan.total_repayment_amount / loan.tenure_months
    principal_part = loan.principal / loan.tenure_months
    interest_part = (loan.total_repayment_amount - loan.principal) / loan.tenure_months
    for i in range(1, loan.tenure_months + 1):
        RepaymentSchedule.objects.create(
            loan=loan,
            installment_number=i,
            due_date=(timezone.now() + relativedelta(months=i)).date(),
            principal_amount=principal_part,
            interest_amount=interest_part,
            total_amount=installment_total,
        )
    return loan
