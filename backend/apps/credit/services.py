from decimal import Decimal
from apps.credit.models import CreditAssessment, EligibilityDecisionStatus


BUCKET_RULES = {
    'SALARIED_LOCAL': {
        'score': 75,
        'decision': EligibilityDecisionStatus.ELIGIBLE,
        'multiplier': Decimal('10'),
        'reason': 'Stable Nigerian salaried user',
    },
    'BUSINESS_LOCAL': {
        'score': 65,
        'decision': EligibilityDecisionStatus.ELIGIBLE,
        'multiplier': Decimal('0.35'),
        'reason': 'Local business cashflow based',
    },
    'SALARIED_DIASPORA': {
        'score': 60,
        'decision': EligibilityDecisionStatus.REVIEW,
        'multiplier': Decimal('6'),
        'reason': 'Diaspora salaried - moderate confidence and manual review',
    },
    'BUSINESS_DIASPORA': {
        'score': 50,
        'decision': EligibilityDecisionStatus.REVIEW,
        'multiplier': Decimal('0.25'),
        'reason': 'Diaspora business - higher risk manual review',
    },
}


def evaluate_credit(user):
    profile = user.profile
    bucket = profile.risk_bucket()
    rule = BUCKET_RULES[bucket]

    if bucket.startswith('SALARIED'):
        max_loan = profile.monthly_income * rule['multiplier']
        monthly_income = profile.monthly_income
    else:
        max_loan = profile.average_monthly_turnover * rule['multiplier']
        monthly_income = profile.monthly_income

    return CreditAssessment.objects.create(
        user=user,
        score=rule['score'],
        monthly_income=monthly_income,
        debt_to_income_ratio=Decimal('0'),
        max_loan_amount=max_loan,
        decision=rule['decision'],
        reason=rule['reason'],
    )
