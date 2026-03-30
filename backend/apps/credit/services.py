from decimal import Decimal
from apps.credit.models import CreditAssessment, EligibilityDecisionStatus


def evaluate_credit(user):
    profile = user.profile
    bucket = profile.risk_bucket()
    score = 0
    max_loan = Decimal('0')
    reason = ''

    if bucket == 'SALARIED_LOCAL':
        score = 75
        max_loan = profile.monthly_income * Decimal('10')
        reason = 'Stable Nigerian salaried user'
    elif bucket == 'BUSINESS_LOCAL':
        score = 65
        max_loan = profile.average_monthly_turnover * Decimal('0.35')
        reason = 'Local business cashflow based'
    elif bucket == 'SALARIED_DIASPORA':
        score = 60
        max_loan = profile.monthly_income * Decimal('6')
        reason = 'Diaspora salaried - moderate confidence'
    elif bucket == 'BUSINESS_DIASPORA':
        score = 50
        max_loan = profile.average_monthly_turnover * Decimal('0.25')
        reason = 'Diaspora business - higher risk'

    decision = EligibilityDecisionStatus.ELIGIBLE if score >= 60 else EligibilityDecisionStatus.REVIEW
    return CreditAssessment.objects.create(
        user=user,
        score=score,
        monthly_income=profile.monthly_income,
        debt_to_income_ratio=Decimal('0'),
        max_loan_amount=max_loan,
        decision=decision,
        reason=reason,
    )
