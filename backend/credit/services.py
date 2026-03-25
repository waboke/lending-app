from .models import CreditScore
from .utils import calculate_credit_score


def update_credit_score(user):
    score = calculate_credit_score(user)

    credit, created = CreditScore.objects.get_or_create(user=user)
    credit.score = score

    # Categorize
    if score >= 700:
        credit.category = "excellent"
    elif score >= 600:
        credit.category = "good"
    elif score >= 500:
        credit.category = "fair"
    else:
        credit.category = "poor"

    credit.save()
    return credit