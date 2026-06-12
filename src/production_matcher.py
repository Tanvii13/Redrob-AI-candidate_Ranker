def get_production_score(candidate):

    score = 0

    for job in candidate["career_history"]:

        text = job["description"].lower()

        keywords = [
            "production",
            "pipeline",
            "airflow",
            "spark",
            "kafka",
            "warehouse",
            "real-time"
        ]

        for keyword in keywords:

            if keyword in text:
                score += 10

    return min(score, 100)