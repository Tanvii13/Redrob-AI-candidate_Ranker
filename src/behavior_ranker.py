def get_behavior_score(candidate):

    signals = candidate["redrob_signals"]

    score = 0

    if signals["open_to_work_flag"]:
        score += 30

    score += min(
        signals["profile_completeness_score"] / 2,
        30
    )

    score += min(
        signals["github_activity_score"] * 2,
        20
    )

    score += min(
        signals["interview_completion_rate"] * 20,
        20
    )

    return score