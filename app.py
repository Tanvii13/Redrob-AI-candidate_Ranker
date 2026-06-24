import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Redrob AI Candidate Ranker",
    layout="wide"
)

st.title("Redrob AI Candidate Ranker")

st.markdown("""
### Intelligent Candidate Discovery & Ranking

This system ranks candidates using:

- Semantic relevance
- AI/ML skill matching
- Experience scoring
- Production readiness signals
- Behavioral indicators

Built for the Redrob Intelligent Candidate Discovery Challenge.
""")

try:

    df = pd.read_csv("outputs/submission.csv")

    st.success("Top 100 candidate ranking loaded")

    st.metric(
        "Candidates Ranked",
        len(df)
    )

    st.subheader("Top 20 Candidates")

    st.dataframe(
        df.head(20),
        use_container_width=True
    )

    st.download_button(
        "Download Submission CSV",
        df.to_csv(index=False),
        file_name="submission.csv",
        mime="text/csv"
    )

except Exception as e:

    st.error(str(e))