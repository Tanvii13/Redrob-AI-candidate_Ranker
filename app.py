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

# Display index from 1
df.index = range(1, len(df) + 1)

st.success("Top 100 candidate ranking loaded")

st.metric(
    "Candidates Ranked",
    len(df)
)

st.subheader("Top 20 Candidates")

st.dataframe(
    df.head(20),
    height=500,
    use_container_width=False
)

st.subheader("Candidate Reasoning")

for _, row in df.head(20).iterrows():

    with st.expander(
        f"Rank #{row['rank']} | Score: {row['score']}"
    ):
        st.write(row["reasoning"])

st.download_button(
    "Download Submission CSV",
    df.to_csv(index=False),
    file_name="submission.csv",
    mime="text/csv"
)