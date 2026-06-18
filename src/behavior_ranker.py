def get_behavior_score(candidate):
    signals = candidate["redrob_signals"]

    score = 0

    if signals["open_to_work_flag"]:
        score += 25

    score += min(signals["profile_completeness_score"] * 0.20, 20)

    github_score = max(signals["github_activity_score"], 0)
    score += min(github_score * 0.20, 20)

    score += min(signals["interview_completion_rate"] * 15, 15)
    score += min(signals["recruiter_response_rate"] * 10, 10)

    if signals["verified_email"]:
        score += 3

    if signals["verified_phone"]:
        score += 3

    if signals["linkedin_connected"]:
        score += 4

    return min(score, 100)
