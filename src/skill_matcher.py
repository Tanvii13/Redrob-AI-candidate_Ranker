def get_skill_score(candidate):
    skills = candidate.get("skills", [])

    ai_skills = [
        "NLP",
        "Fine-tuning LLMs",
        "Machine Learning",
        "Deep Learning",
        "PyTorch",
        "TensorFlow",
        "Computer Vision",
        "Speech Recognition",
        "Image Classification",
        "LoRA",
        "Milvus"
    ]

    score = 0

    for skill in skills:
        if skill["name"] in ai_skills:
            score += 10

    return min(score, 100)