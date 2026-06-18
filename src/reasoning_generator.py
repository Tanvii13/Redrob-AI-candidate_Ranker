def generate_reasoning(candidate, semantic, skill, experience, production, behavior, rank):
    """
    Generate specific, honest, fact-based reasoning for each candidate.
    References actual profile data — no hallucination.
    Tone matches rank: positive for top, honest-concern for bottom.
    """

    profile = candidate["profile"]
    signals = candidate["redrob_signals"]

    years = profile["years_of_experience"]
    title = profile["current_title"]
    company = profile["current_company"]
    location = profile.get("location", "")
    notice = signals.get("notice_period_days", None)
    relocate = signals.get("willing_to_relocate", False)
    github = signals.get("github_activity_score", -1)
    work_mode = signals.get("preferred_work_mode", "")
    assessment_scores = signals.get("skill_assessment_scores", {})

    # --- Part 1: Opening — who is this person ---

    opening = (
        f"{title} at {company} with {years} years of experience"
    )

    # --- Part 2: Strengths ---

    strengths = []

    # AI skill match
    ai_skills = [
        "NLP", "Fine-tuning LLMs", "Machine Learning",
        "Deep Learning", "PyTorch", "TensorFlow",
        "Computer Vision", "Speech Recognition",
        "Image Classification", "LoRA", "Milvus"
    ]
    matched_skills = [
        s["name"] for s in candidate.get("skills", [])
        if s["name"] in ai_skills
    ]
    if matched_skills:
        strengths.append(
            f"relevant AI/ML skills: {', '.join(matched_skills[:3])}"
        )

    # Skill assessment scores (actual test results — very specific)
    strong_assessments = [
        f"{k} ({round(v)}%)"
        for k, v in assessment_scores.items()
        if v >= 60
    ]
    if strong_assessments:
        strengths.append(
            f"assessed proficiency in {', '.join(strong_assessments[:2])}"
        )

    # Production experience
    if production >= 40:
        strengths.append("hands-on production pipeline experience")
    elif production >= 20:
        strengths.append("some production/data pipeline exposure")

    # GitHub activity
    if github > 7:
        strengths.append("active GitHub presence")

    # Behavioral signals
    if signals.get("open_to_work_flag"):
        strengths.append("actively looking")

    # Location / relocation
    if location:
        if relocate:
            strengths.append(f"based in {location}, willing to relocate")
        else:
            strengths.append(f"based in {location}")

    # --- Part 3: Concerns (honest, rank-appropriate) ---

    concerns = []

    # Notice period
    if notice and notice > 90:
        concerns.append(f"long notice period ({notice} days)")

    # No GitHub
    if github == -1 and rank <= 50:
        concerns.append("no GitHub activity detected")

    # Weak AI skills for a top candidate
    if skill < 20 and rank <= 30:
        concerns.append("limited AI/ML skill match for this role")

    # Low semantic match
    if semantic < 0.35 and rank > 50:
        concerns.append("profile not closely aligned with JD")

    # Not open to work
    if not signals.get("open_to_work_flag") and rank <= 40:
        concerns.append("not marked open to work")

    # --- Assemble final reasoning ---

    parts = [opening]

    if strengths:
        parts.append("; ".join(strengths[:3]))

    if concerns:
        parts.append("concern: " + "; ".join(concerns[:2]))

    reasoning = ". ".join(parts) + "."

    # Keep it under ~250 chars for readability
    if len(reasoning) > 260:
        reasoning = reasoning[:257] + "..."

    return reasoning