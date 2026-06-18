import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from main import normalize_scores, reasoning, score_candidate


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "sample_candidates.json"


def load_sample_candidates():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_response():
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

    return {
        "message": "Redrob ranker sandbox using sample_candidates.json",
        "candidate_count": len(candidates),
        "results": results,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(build_response()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
