from decimal import Decimal
from datetime import datetime, timedelta
from apps.credit.models import CreditAssessment, EligibilityDecisionStatus
import requests  # Assuming we use requests for API calls


def verify_nin(nin):
    """Mock NIN verification - in real app, call NIMC API"""
    if not nin or len(nin) != 11:
        return False, "Invalid NIN format"
    # Mock check - assume valid if starts with 1
    if nin.startswith('1'):
        return True, "NIN verified"
    return False, "NIN not found"


def verify_bvn(bvn):
    """Mock BVN verification - in real app, call CBN API"""
    if not bvn or len(bvn) != 11:
        return False, "Invalid BVN format"
    # Mock check
    if bvn.startswith('2'):
        return True, "BVN verified"
    return False, "BVN not found"


def verify_bank_account(account_number, bank_code):
    """Mock bank account verification"""
    if not account_number or len(account_number) != 10:
        return False, "Invalid account number"
    # Mock check
    if account_number.startswith('0'):
        return True, "Account verified"
    return False, "Account not found"


def get_credit_score(bvn):
    """Mock credit score from bureau"""
    # In real app, call CRC API
    if bvn.startswith('2'):
        return 750  # Good score
    return 450  # Poor score


def check_salary_account_activity(account_number, months=2):
    """Check if salary account has been active in last X months"""
    # Mock check - assume active if account starts with 0
    if account_number.startswith('0'):
        return True, "Account active in last 2 months"
    return False, "No activity in last 2 months"


def perform_verifications(user):
    """Perform all required verifications"""
    profile = user.profile
    verifications = {}

    # NIN verification
    if profile.nin:
        verifications['nin'] = verify_nin(profile.nin)
    else:
        verifications['nin'] = (False, "NIN not provided")

    # BVN verification
    if profile.bvn:
        verifications['bvn'] = verify_bvn(profile.bvn)
    else:
        verifications['bvn'] = (False, "BVN not provided")

    # Bank account verification (assuming we have account details)
    # For demo, assume account_number and bank_code are in profile or related model
    # Let's add placeholders
    account_number = getattr(profile, 'account_number', None)
    bank_code = getattr(profile, 'bank_code', None)
    if account_number and bank_code:
        verifications['bank_account'] = verify_bank_account(account_number, bank_code)
    else:
        verifications['bank_account'] = (False, "Bank account details not provided")

    # Credit score
    if profile.bvn:
        verifications['credit_score'] = (True, str(get_credit_score(profile.bvn)))
    else:
        verifications['credit_score'] = (False, "BVN required for credit score")

    # Salary account activity
    if account_number:
        verifications['salary_activity'] = check_salary_account_activity(account_number)
    else:
        verifications['salary_activity'] = (False, "Account details required")

    return verifications


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
