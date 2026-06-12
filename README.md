# Redrob AI Candidate Ranker

AI-powered candidate ranking system built for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

## Features

* Semantic candidate matching using Sentence Transformers
* AI skill matching
* Experience scoring
* Behavioral signal analysis
* Automated candidate ranking
* CSV export of ranked candidates

## Tech Stack

* Python
* Sentence Transformers
* Scikit-learn
* Pandas
* HuggingFace Transformers

## Project Structure

src/ - Core ranking logic

data/ - Candidate and job description data

outputs/ - Ranking results

configs/ - Scoring configuration

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Output

The system generates:

outputs/ranked_candidates.csv

containing ranked candidates and their scores.
