def calculate_final_score(
    semantic,
    skill,
    experience,
    behavior
):

    final_score = (
        semantic * 35 +
        (skill / 100) * 25 +
        (experience / 100) * 10 +
        (behavior / 100) * 15
    )

    return round(final_score, 2)