def get_skill_score(candidate):
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    assessment_scores = signals.get("skill_assessment_scores", {})

    role_skills = {
        "NLP": 10,
        "Fine-tuning LLMs": 12,
        "Machine Learning": 10,
        "Deep Learning": 8,
        "PyTorch": 8,
        "TensorFlow": 6,
        "Computer Vision": 5,
        "Speech Recognition": 5,
        "Image Classification": 4,
        "LoRA": 8,
        "Milvus": 8,
        "Vector Databases": 8,
        "MLOps": 10,
        "Feature Engineering": 6,
        "Statistical Modeling": 5,
        "AWS": 4,
        "GCP": 4,
        "Azure": 4,
        "Docker": 5,
        "Kubernetes": 6,
        "Airflow": 5,
        "Spark": 5,
        "Kafka": 5,
        "Python": 8,
        "SQL": 4
    }

    proficiency_multiplier = {
        "beginner": 0.5,
        "intermediate": 0.75,
        "advanced": 1.0,
        "expert": 1.2
    }

    score = 0

    for skill in skills:
        name = skill.get("name", "")

        if name not in role_skills:
            continue

        proficiency = skill.get("proficiency", "beginner")
        multiplier = proficiency_multiplier.get(proficiency, 0.5)
        duration_months = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)

        score += role_skills[name] * multiplier
        score += min(duration_months / 24, 2)
        score += min(endorsements / 25, 2)

    for skill_name, assessment_score in assessment_scores.items():
        if skill_name in role_skills and assessment_score >= 60:
            score += 5

    return min(score, 100)
