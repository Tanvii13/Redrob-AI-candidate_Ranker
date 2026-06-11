import gzip
import json

def load_candidates(file_path):
    candidates = []

    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                candidates.append(json.loads(line))

    return candidates