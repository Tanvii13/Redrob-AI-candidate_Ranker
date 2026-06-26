import argparse
import csv
import gzip
import json
import math
import os
import re
from datetime import date, datetime
from heapq import heappush, heappushpop

from docx import Document


DEFAULT_CANDIDATES = "data/candidates.jsonl"
DEFAULT_JOB = "data/job_description.docx"
DEFAULT_SUBMISSION = "outputs/submission.csv"
DEFAULT_DEBUG = "outputs/ranked_candidates.csv"
REFERENCE_DATE = date(2026, 6, 1)


ROLE_SKILLS = {
    "NLP": 4.0,
    "Fine-tuning LLMs": 5.0,
    "Machine Learning": 4.0,
    "Deep Learning": 3.5,
    "PyTorch": 3.5,
    "TensorFlow": 2.5,
    "LoRA": 3.5,
    "Milvus": 3.0,
    "MLOps": 4.0,
    "Feature Engineering": 2.5,
    "Statistical Modeling": 2.0,
    "Python": 3.0,
    "SQL": 1.5,
    "Spark": 2.5,
    "Kafka": 2.0,
    "Airflow": 2.0,
    "Docker": 2.0,
    "Kubernetes": 2.0,
    "AWS": 1.5,
    "GCP": 1.5,
    "Azure": 1.5,
}

PROFICIENCY_MULTIPLIER = {
    "beginner": 0.45,
    "intermediate": 0.75,
    "advanced": 1.0,
    "expert": 1.2,
}

STRONG_AI_TITLES = (
    "ai engineer",
    "machine learning engineer",
    "ml engineer",
    "senior machine learning engineer",
    "applied scientist",
    "data scientist",
    "nlp engineer",
    "search engineer",
    "recommendation engineer",
    "relevance engineer",
    "ranking engineer",
    "retrieval engineer",
    "staff machine learning engineer",
    "principal machine learning engineer",
    "senior data scientist",
    )

ADJACENT_TECH_TITLES = (
    "data engineer",
    "backend engineer",
    "software engineer",
    "analytics engineer",
    "platform engineer",
    "mlops engineer",
)

NON_TECH_TITLES = (
    "marketing manager",
    "hr manager",
    "sales executive",
    "graphic designer",
    "content writer",
    "accountant",
    "customer support",
    "mechanical engineer",
    "civil engineer",
    "operations manager",
)

SYSTEM_EVIDENCE = {
    "ranking": 3.0,
    "recommendation": 3.0,
    "recommender": 3.0,
    "retrieval": 3.0,
    "search": 2.5,
    "semantic search": 3.5,
    "vector": 2.2,
    "embedding": 2.2,
    "rag": 3.5,
    "llm": 2.8,
    "fine-tun": 2.5,
    "model evaluation": 2.4,
    "eval framework": 2.8,
    "production": 2.2,
    "deployed": 2.0,
    "real-time": 1.8,
    "pipeline": 1.6,
    "feature pipeline": 2.2,
    "spark": 1.5,
    "kafka": 1.5,
    "airflow": 1.3,
    "scale": 1.6,
    "users": 1.2,
    "recommendation engine": 4.0,
    "recommendation system": 4.0,
    "matching system": 4.0,
    "candidate matching": 4.0,
    "ranking model": 4.0,
    "learning to rank": 4.0,
    "ltr": 3.0,
    "ndcg": 4.0,
    "mrr": 3.5,
    "map": 3.5,
    "a/b testing": 3.0,
    "ab testing": 3.0,
    "offline evaluation": 3.0,
    "online evaluation": 3.0,
    "relevance": 3.0,
}

PRODUCT_COMPANY_HINTS = (
    "product",
    "saas",
    "platform",
    "marketplace",
    "user",
    "customers",
    "growth",
    "metrics",
    "a/b",
)

TIER1_INDIAN_CITIES = (
    "bengaluru",
    "bangalore",
    "delhi",
    "new delhi",
    "noida",
    "pune",
    "mumbai",
    "hyderabad",
    "chennai",
    "gurgaon",
    "gurugram",
)

CONSULTING_COMPANIES = (
    "tcs",
    "infosys",
    "wipro",
    "cognizant",
    "accenture",
    "capgemini"
)

def load_job_text(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def open_candidates(path):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def normalize(text):
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def contains_any(text, phrases):
    return any(phrase in text for phrase in phrases)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None


def months_since(value):
    parsed = parse_date(value)
    if not parsed:
        return 999
    return max(0, (REFERENCE_DATE.year - parsed.year) * 12 + REFERENCE_DATE.month - parsed.month)


def clamp(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def profile_text(candidate):
    profile = candidate["profile"]
    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_industry", ""),
    ]

    for job in candidate.get("career_history", []):
        parts.extend([
            job.get("title", ""),
            job.get("industry", ""),
            job.get("description", ""),
        ])

    parts.extend(skill.get("name", "") for skill in candidate.get("skills", []))
    return normalize(" ".join(parts))


def title_score(candidate):
    profile = candidate["profile"]
    current_title = normalize(profile.get("current_title", ""))
    history_titles = normalize(" ".join(job.get("title", "") for job in candidate.get("career_history", [])))

    if contains_any(current_title, STRONG_AI_TITLES):
        return 16
    if contains_any(history_titles, STRONG_AI_TITLES):
        return 13
    if contains_any(current_title, ADJACENT_TECH_TITLES):
        return 10
    if contains_any(history_titles, ADJACENT_TECH_TITLES):
        return 8
    if contains_any(current_title, NON_TECH_TITLES):
        return 1
    return 4


def career_system_score(text):
    score = 0.0
    for phrase, weight in SYSTEM_EVIDENCE.items():
        if phrase in text:
            score += weight

    product_hits = sum(1 for phrase in PRODUCT_COMPANY_HINTS if phrase in text)
    score += min(product_hits * 1.2, 5)

    return clamp(score, 0, 24)


def skill_score(candidate, support_score):
    score = 0.0
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    assessments = signals.get("skill_assessment_scores", {})

    expert_zero_duration = 0

    for skill in skills:
        name = skill.get("name", "")
        if name not in ROLE_SKILLS:
            continue

        proficiency = skill.get("proficiency", "beginner")
        duration = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)

        if proficiency == "expert" and duration == 0:
            expert_zero_duration += 1

        score += ROLE_SKILLS[name] * PROFICIENCY_MULTIPLIER.get(proficiency, 0.45)
        score += min(duration / 36, 1.5)
        score += min(endorsements / 50, 1.0)

    for name, assessment in assessments.items():
        if name in ROLE_SKILLS and assessment >= 60:
            score += 2.5

    # The JD warns that keyword-stuffed skills are a trap. Skills matter most
    # when the title/career history also supports an AI/product engineering fit.
    if support_score < 10:
        score *= 0.45
    elif support_score < 18:
        score *= 0.75

    if expert_zero_duration >= 5:
        score *= 0.45

    return clamp(score, 0, 18)


def experience_score(candidate):
    years = float(candidate["profile"].get("years_of_experience", 0))

    if 6 <= years <= 8:
        return 14

    if 5 <= years < 6:
        return 12

    if 8 < years <= 9:
        return 12

    if 4 <= years < 5:
        return 8

    if 9 < years <= 11:
        return 8

    if 3 <= years < 4:
        return 4

    return 1


def behavior_score(candidate):
    signals = candidate["redrob_signals"]
    score = 0.0

    if signals.get("open_to_work_flag"):
        score += 4

    last_active_months = months_since(signals.get("last_active_date"))
    if last_active_months <= 1:
        score += 4
    elif last_active_months <= 3:
        score += 2.5
    elif last_active_months > 6:
        score -= 3

    score += min(signals.get("recruiter_response_rate", 0) * 4, 4)
    score += min(signals.get("interview_completion_rate", 0) * 3, 3)
    score += min(max(signals.get("github_activity_score", -1), 0) / 100 * 3, 3)
    github_score = signals.get("github_activity_score", -1)

    if github_score > 70:
        score += 2

    if github_score > 90:
        score += 2
    score += min(signals.get("saved_by_recruiters_30d", 0) / 8 * 2, 2)
    score += min(signals.get("profile_completeness_score", 0) / 100 * 2, 2)

    if signals.get("verified_email"):
        score += 0.5
    if signals.get("verified_phone"):
        score += 0.5
    if signals.get("linkedin_connected"):
        score += 0.5

    notice = signals.get("notice_period_days", 180)
    if notice <= 30:
        score += 1
    elif notice > 90:
        score -= 2

    if (
    signals.get("recruiter_response_rate", 0) < 0.05
    and last_active_months > 6
    ):
        score -= 4
    return clamp(score, 0, 18)


def location_score(candidate):
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    location = normalize(profile.get("location", ""))
    country = normalize(profile.get("country", ""))

    score = 0.0
    if "india" in country:
        score += 2
    if contains_any(location, ("pune", "noida")):
        score += 5
    elif contains_any(location, TIER1_INDIAN_CITIES):
        score += 3
    if signals.get("willing_to_relocate"):
        score += 2
    if signals.get("preferred_work_mode") in {"hybrid", "flexible", "onsite"}:
        score += 1

    return clamp(score, 0, 8)


def honeypot_penalty(candidate):
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    years = float(profile.get("years_of_experience", 0))
    jobs = candidate.get("career_history", [])
    skills = candidate.get("skills", [])

    penalty = 0.0

    total_job_years = sum(job.get("duration_months", 0) for job in jobs) / 12
    if years - total_job_years > 3:
        penalty += 15

    expert_zero_duration = sum(
        1
        for skill in skills
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 0) == 0
    )
    if expert_zero_duration >= 5:
        penalty += 25

    strong_skill_count = sum(
        1
        for skill in skills
        if skill.get("name") in ROLE_SKILLS and skill.get("proficiency") in {"advanced", "expert"}
    )
    current_title = normalize(profile.get("current_title", ""))
    history_titles = normalize(" ".join(job.get("title", "") for job in jobs))
    has_tech_title = contains_any(current_title + " " + history_titles, STRONG_AI_TITLES + ADJACENT_TECH_TITLES)

    if strong_skill_count >= 8 and not has_tech_title:
        penalty += 18

    if signals.get("github_activity_score", 0) > 95 and not has_tech_title:
        penalty += 8

    consulting_count = 0

    for job in jobs:
        company = normalize(job.get("company_name", ""))

        if contains_any(company, CONSULTING_COMPANIES):
            consulting_count += 1

    if len(jobs) > 0 and consulting_count == len(jobs):
        penalty += 8

    if years < 3 and strong_skill_count > 10:
        penalty += 20

    return penalty


def score_candidate(candidate):
    text = profile_text(candidate)
    title = title_score(candidate)
    career = career_system_score(text)
    support = title + career

    skills = skill_score(candidate, support)
    experience = experience_score(candidate)
    behavior = behavior_score(candidate)
    location = location_score(candidate)
    penalty = honeypot_penalty(candidate)

    raw_score = title + career + skills + experience + behavior + location - penalty
    score = clamp(raw_score, 0, 100)

    return {
        "candidate_id": candidate["candidate_id"],
        "name": candidate["profile"]["anonymized_name"],
        "score": round(score, 6),
        "title_score": round(title, 2),
        "career_score": round(career, 2),
        "skill_score": round(skills, 2),
        "experience_score": round(experience, 2),
        "behavior_score": round(behavior, 2),
        "location_score": round(location, 2),
        "penalty": round(penalty, 2),
    }


def reasoning(candidate, scored):
    profile = candidate["profile"]
    signals = candidate["redrob_signals"]
    years = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "Candidate")

    strengths = []
    concerns = []

    if scored["title_score"] >= 13:
        strengths.append("direct AI/ML title fit")
    elif scored["title_score"] >= 8:
        strengths.append("adjacent engineering background")

    if scored["career_score"] >= 14:
        strengths.append("career evidence of ranking/retrieval or production ML systems")
    elif scored["career_score"] >= 8:
        strengths.append("some production data/ML system exposure")

    matched_skills = [
        s.get("name", "")
        for s in candidate.get("skills", [])
        if s.get("name", "") in ROLE_SKILLS
    ]
    if matched_skills:
        strengths.append("relevant skills: " + ", ".join(matched_skills[:3]))

    if signals.get("open_to_work_flag") and months_since(signals.get("last_active_date")) <= 3:
        strengths.append("active and open to work")

    if not signals.get("open_to_work_flag"):
        concerns.append("not marked open to work")
    if signals.get("notice_period_days", 0) > 90:
        concerns.append(f"{signals['notice_period_days']}-day notice period")
    if scored["penalty"] > 0:
        concerns.append("profile consistency risk")

    sentence = f"{title} with {years} years of experience"
    if strengths:
        sentence += "; " + "; ".join(strengths[:3])
    if concerns:
        sentence += "; concern: " + "; ".join(concerns[:2])
    return sentence[:300] + "."


def read_candidates_with_scores(path, top_n):
    heap = []
    kept_candidates = {}
    total = 0

    with open_candidates(path) as handle:
        for line in handle:
            if not line.strip():
                continue

            candidate = json.loads(line)
            scored = score_candidate(candidate)
            total += 1

            # Heap keeps only the best top_n candidates in memory.
            heap_item = (scored["score"], scored["candidate_id"], scored)
            if len(heap) < top_n:
                heappush(heap, heap_item)
                kept_candidates[scored["candidate_id"]] = candidate
            elif heap_item > heap[0]:
                removed = heappushpop(heap, heap_item)
                kept_candidates.pop(removed[2]["candidate_id"], None)
                kept_candidates[scored["candidate_id"]] = candidate

    ranked = [item[2] for item in heap]
    ranked.sort(key=lambda row: (-row["score"], row["candidate_id"]))
    return total, ranked, kept_candidates


def normalize_scores(ranked):
    if not ranked:
        return []

    max_score = ranked[0]["score"]
    min_score = ranked[-1]["score"]
    spread = max(max_score - min_score, 1e-9)

    normalized = []
    for row in ranked:
        scaled = 0.2 + 0.8 * ((row["score"] - min_score) / spread)
        row = dict(row)
        scaled -= (len(normalized) * 0.00001)
        row["normalized_score"] = round(scaled, 4)
        normalized.append(row)

    return normalized


def write_outputs(ranked, kept_candidates, submission_path, debug_path):
    os.makedirs(os.path.dirname(submission_path) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(debug_path) or ".", exist_ok=True)

    normalized = normalize_scores(ranked)

    with open(submission_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()

        for rank, row in enumerate(normalized, start=1):
            candidate = kept_candidates[row["candidate_id"]]
            writer.writerow({
                "candidate_id": row["candidate_id"],
                "rank": rank,
                "score": row["normalized_score"],
                "reasoning": reasoning(candidate, row),
            })

    with open(debug_path, "w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "candidate_id",
            "name",
            "score",
            "title_score",
            "career_score",
            "skill_score",
            "experience_score",
            "behavior_score",
            "location_score",
            "penalty",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ranked)


def parse_args():
    parser = argparse.ArgumentParser(description="Rank Redrob candidates for the hackathon submission.")
    parser.add_argument("--candidates", default=DEFAULT_CANDIDATES, help="Path to candidates.jsonl or candidates.jsonl.gz")
    parser.add_argument("--job", default=DEFAULT_JOB, help="Path to job_description.docx")
    parser.add_argument("--out", default=DEFAULT_SUBMISSION, help="Output submission CSV path")
    parser.add_argument("--debug-out", default=DEFAULT_DEBUG, help="Detailed debug ranking CSV path")
    parser.add_argument("--top-n", type=int, default=100, help="Number of candidates to submit")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.top_n != 100:
        raise ValueError("Challenge submission must contain exactly 100 candidates.")

    # Load the JD so the run documents the actual role file used. The scorer is
    # intentionally local and deterministic rather than calling external models.
    job_text = load_job_text(args.job)
    print(f"Loaded job description ({len(job_text)} characters).")

    total, ranked, kept_candidates = read_candidates_with_scores(args.candidates, args.top_n)

    if len(ranked) != 100:
        raise ValueError(f"Expected 100 ranked candidates, found {len(ranked)}.")

    write_outputs(ranked, kept_candidates, args.out, args.debug_out)

    print(f"Read {total} candidates.")
    print(f"Submission saved to {args.out}")
    print(f"Detailed ranking saved to {args.debug_out}")


if __name__ == "__main__":
    main()
