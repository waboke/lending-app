def calculate_credit_score(user):
    score = 300  # base score

    profile = user.profile

    # Category-based scoring
    if profile.category == "military":
        score += 200
    elif profile.category == "paramilitary":
        score += 150
    elif profile.category == "civil_servant":
        score += 100
    elif profile.category == "businessman":
        score += 120

    # Example extra checks
    if profile.phone_number:
        score += 50

    return score