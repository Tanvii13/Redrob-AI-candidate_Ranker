# 🤖 Redrob AI Candidate Ranker

An AI-powered candidate discovery and ranking system built for the **Redrob Intelligent Candidate Discovery & Ranking Challenge**.

---

## Overview

This project automatically ranks candidates by combining semantic AI matching with skill, experience, behavioral, and production engineering scoring.

Instead of relying only on keyword matching, the system understands the meaning of the candidate profile using Sentence Transformers and produces a weighted final score.

---

## Features

* Semantic similarity matching using Sentence Transformers
* AI skill matching
* Experience scoring
* Behavioral scoring
* Production pipeline experience scoring
* Weighted candidate ranking
* Automatic CSV export

---

## Tech Stack

* Python
* Sentence Transformers
* HuggingFace Transformers
* Scikit-learn
* Pandas
* NumPy
* python-docx

---

## Ranking Strategy

| Metric                | Weight |
| --------------------- | ------ |
| Semantic Matching     | 40%    |
| Skill Score           | 20%    |
| Experience Score      | 10%    |
| Behavioral Score      | 15%    |
| Production Experience | 15%    |

---

## Project Structure

```text
Redrob-AI-candidate_Ranker/

├── data/
├── outputs/
├── src/
│   ├── semantic_ranker.py
│   ├── skill_matcher.py
│   ├── experience_matcher.py
│   ├── production_matcher.py
│   ├── behavior_ranker.py
│   ├── final_ranker.py
│   ├── text_builder.py
│   └── job_loader.py
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

---

## Output

The system generates:

```
outputs/ranked_candidates.csv
```

containing:

* Candidate ID
* Candidate Name
* Semantic Score
* Skill Score
* Experience Score
* Production Score
* Behavioral Score
* Final Score

---

## Future Improvements

* Resume PDF parsing
* LLM-based skill extraction
* Explainable AI ranking
* Dynamic scoring configuration
* REST API deployment
* Streamlit dashboard

---

## Author

Tanvi
