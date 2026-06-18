# Redrob AI Candidate Ranker

This repository contains a fast, local candidate ranking system for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

The ranker produces the required top-100 CSV:

```text
candidate_id,rank,score,reasoning
```

## Approach

The challenge JD asks for a Senior AI Engineer for a founding team. The system ranks candidates using a deterministic hybrid score instead of slow per-candidate LLM calls.

It considers:

- AI/ML and adjacent engineering title fit
- Career evidence of retrieval, ranking, recommendation, search, LLM, evaluation, and production ML systems
- Relevant skill strength using proficiency, duration, endorsements, and assessment scores
- Experience fit, with 5-9 years preferred
- Behavioral/availability signals such as open-to-work, last active date, recruiter response rate, interview completion, saved-by-recruiters, verification, and notice period
- Location fit for Pune/Noida/hybrid and relocation
- Consistency penalties for likely honeypot or keyword-stuffed profiles

The ranking step is CPU-only, local, deterministic, and does not call hosted APIs or download models.

## Project Structure

```text
Redrob-AI-candidate_Ranker/
  data/
    candidates.jsonl
    job_description.docx
    validate_submission.py
  outputs/
    submission.csv
    ranked_candidates.csv
  main.py
  requirements.txt
  README.md
```

## Setup

```powershell
cd "C:\Users\tanvi\Desktop\vs_code\Redrob-AI-candidate_Ranker"
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

This writes:

```text
outputs/submission.csv
outputs/ranked_candidates.csv
```

You can also run with explicit paths:

```powershell
python main.py --candidates data/candidates.jsonl --job data/job_description.docx --out outputs/submission.csv
```

## Validate

```powershell
python data\validate_submission.py outputs\submission.csv
```

Expected output:

```text
Submission is valid.
```

## Vercel Sandbox

This repo also includes a lightweight Vercel sandbox:

- `index.html` shows a simple demo UI.
- `api/rank.py` ranks `data/sample_candidates.json`.
- The sandbox is for reviewer/demo use only; the full submission is still produced locally with `python main.py`.

Deploy the same GitHub repo to Vercel, then use the Vercel project URL as the `sandbox_link` in `submission_metadata.yaml`.

## Notes

- The organizer-provided files are used as inputs only.
- The final upload CSV should be renamed to your registered participant/team ID if the portal requires that filename.
- The sample submission is only a format example and is not used for ranking.
