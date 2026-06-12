import json

def load_sample_candidates(path):

    with open(path, "r", encoding="utf-8") as file:

        candidates = json.load(file)

    return candidates