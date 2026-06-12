from src.data_loader import load_sample_candidates
from src.job_loader import load_job_description
from src.text_builder import build_candidate_text
from src.semantic_ranker import get_semantic_score

from src.skill_matcher import get_skill_score
from src.experience_matcher import get_experience_score
from src.behavior_ranker import get_behavior_score
from src.final_ranker import calculate_final_score

import pandas as pd


candidates = load_sample_candidates(
    "data/sample_candidates.json"
)

jd_text = load_job_description(
    "data/job_description.docx"
)

results = []

for candidate in candidates:

    candidate_text = build_candidate_text(
        candidate
    )

    semantic = get_semantic_score(
        jd_text,
        candidate_text
    )

    skill = get_skill_score(
        candidate
    )

    experience = get_experience_score(
        candidate
    )

    behavior = get_behavior_score(
        candidate
    )

    final_score = calculate_final_score(
        semantic,
        skill,
        experience,
        behavior
    )

    results.append({
        "candidate_id":
            candidate["candidate_id"],

        "name":
            candidate["profile"]["anonymized_name"],

        "semantic":
            round(semantic, 4),

        "skill":
            skill,

        "experience":
            experience,

        "behavior":
            behavior,

        "final_score":
            final_score
    })

results.sort(
    key=lambda x: x["final_score"],
    reverse=True
)

print("\nTOP 10 CANDIDATES\n")

for i, candidate in enumerate(
    results[:10],
    start=1
):
    print(
        f"{i}. "
        f"{candidate['candidate_id']} | "
        f"{candidate['name']} | "
        f"Score={candidate['final_score']}"
    )

df = pd.DataFrame(results)

df.to_csv(
    "outputs/ranked_candidates.csv",
    index=False
)

print(
    "\nResults saved to outputs/ranked_candidates.csv"
)