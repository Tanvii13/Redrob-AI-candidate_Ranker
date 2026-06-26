import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Redrob AI Candidate Ranker",
    layout="wide"
)

st.title("Redrob AI Candidate Ranker")

st.markdown("""
### Intelligent Candidate Discovery & Ranking System

This project ranks candidates for the Senior AI Engineer role using:

- AI/ML title relevance
- Retrieval & ranking system experience
- Production ML evidence
- Skill strength & assessments
- Behavioral availability signals
- Location fit
- Honeypot detection

Built for the Redrob Hackathon.
""")

df = pd.read_csv("outputs/submission.csv")

st.metric("Candidates Ranked", len(df))

st.subheader("Top 10 Candidates")

for _, row in df.head(10).iterrows():

    with st.expander(
        f"Rank #{row['rank']} | {row['candidate_id']}"
    ):
        st.write(f"Score: {row['score']}")
        st.write(row["reasoning"])

st.subheader("Top 100 Rankings")

st.dataframe(
    df,
    use_container_width=True
)

st.download_button(
    "Download Submission CSV",
    df.to_csv(index=False),
    file_name="submission.csv",
    mime="text/csv"
)