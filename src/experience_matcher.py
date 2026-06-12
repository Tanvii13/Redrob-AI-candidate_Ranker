def get_experience_score(candidate):
    years = candidate["profile"]["years_of_experience"]

    if 5 <= years <= 9:
        return 100

    elif 3 <= years < 5:
        return 70

    elif 9 < years <= 12:
        return 70

    return 40