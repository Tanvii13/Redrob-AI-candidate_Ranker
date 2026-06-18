import csv
import json
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from main import normalize_scores, reasoning, score_candidate


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "data" / "sample_candidates.json"
SUBMISSION_PATH = ROOT / "outputs" / "submission.csv"
TOP100_DEMO_PATH = ROOT / "outputs" / "top100_demo.json"


def load_sample_candidates():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_sample_response(limit):
    candidates = load_sample_candidates()
    scored = []
    kept_candidates = {}

    for candidate in candidates:
        row = score_candidate(candidate)
        scored.append(row)
        kept_candidates[row["candidate_id"]] = candidate

    safe_limit = max(1, min(limit, len(scored)))
    scored.sort(key=lambda row: (-row["score"], row["candidate_id"]))
    top_rows = normalize_scores(scored[:safe_limit])

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
        "message": "Sample sandbox ranking from data/sample_candidates.json",
        "source": "sample",
        "candidate_count": len(candidates),
        "display_count": len(results),
        "results": results,
    }


def build_submission_response():
    if TOP100_DEMO_PATH.exists():
        with open(TOP100_DEMO_PATH, "r", encoding="utf-8") as handle:
            results = json.load(handle)
        results.sort(key=lambda row: row["rank"])
        return {
            "message": "Final validated top-100 submission with demo display metadata",
            "source": "submission",
            "candidate_count": 100000,
            "display_count": len(results),
            "results": results,
        }

    results = []
    with open(SUBMISSION_PATH, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            results.append({
                "rank": int(row["rank"]),
                "candidate_id": row["candidate_id"],
                "name": "",
                "score": row["score"],
                "reasoning": row["reasoning"],
            })

    results.sort(key=lambda row: row["rank"])
    return {
        "message": "Final validated top-100 submission from outputs/submission.csv",
        "source": "submission",
        "candidate_count": 100000,
        "display_count": len(results),
        "results": results,
    }


def build_response(path):
    query = parse_qs(urlparse(path).query)
    view = query.get("view", ["sample10"])[0]

    if view == "sample50":
        return build_sample_response(50)
    if view == "submission100":
        return build_submission_response()
    return build_sample_response(10)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(build_response(self.path)).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
