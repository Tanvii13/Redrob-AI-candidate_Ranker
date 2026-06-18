import json

def load_sample_candidates(path):

    candidates = []

    with open(path, "r", encoding="utf-8") as file:

        if path.endswith(".jsonl"):

            for line in file:

                if line.strip():

                    candidates.append(json.loads(line))

        else:

            candidates = json.load(file)

    return candidates