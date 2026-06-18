import json
from pathlib import Path

from main import normalize_scores, reasoning, score_candidate


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "sample_candidates.json"


def load_sample_candidates():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def handler(request):
    candidates = load_sample_candidates()
    scored = []
    kept_candidates = {}

    for candidate in candidates:
        row = score_candidate(candidate)
        scored.append(row)
        kept_candidates[row["candidate_id"]] = candidate

    scored.sort(key=lambda row: (-row["score"], row["candidate_id"]))
    top_rows = normalize_scores(scored[:10])

    results = []
    for rank, row in enumerate(top_rows, start=1):
        candidate = kept_candidates[row["candidate_id"]]
        results.append({
            "rank": rank,
            "candidate_id": row["candidate_id"],
            "name": row["name"],
            "score": row["normalized_score"],
            "reasoning": reasoning(candidate, row),
        })

    body = json.dumps({
        "message": "Redrob ranker sandbox using sample_candidates.json",
        "candidate_count": len(candidates),
        "results": results,
    })

    return body, 200, {"content-type": "application/json; charset=utf-8"}
