def calculate_final_score(
    semantic,
    skill,
    experience,
    behavior,
    production
):

    final_score = (
        semantic * 40 +
        (skill / 100) * 20 +
        (experience / 100) * 10 +
        (behavior / 100) * 15 +
        (production / 100) * 15
    )

    return round(final_score, 2)