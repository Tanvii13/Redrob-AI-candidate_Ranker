import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Redrob AI Candidate Ranker",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Redrob AI Candidate Ranker")

st.markdown("""
### Intelligent Candidate Discovery & Ranking System

This sandbox demonstrates a deterministic ranking system built for the
**Redrob Senior AI Engineer Hiring Challenge**.

The ranking model evaluates:

- AI/ML title relevance
- Retrieval, search and ranking system experience
- Production ML engineering evidence
- Skill strength and assessment performance
- Experience fit for the target role
- Behavioral hiring signals
- Location and relocation preferences
- Profile consistency and honeypot detection

No external APIs, hosted LLMs, or network calls are used during ranking.
""")

st.info(
    "100,000 candidate profiles were evaluated and the top 100 candidates "
    "were selected using a deterministic weighted scoring framework."
)

st.divider()

try:
    df = pd.read_csv("outputs/submission.csv")

    st.success("✅ Top 100 candidate ranking loaded successfully")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Candidates Ranked",
            len(df)
        )

    with col2:
        st.metric(
            "Top Candidate Score",
            round(float(df.iloc[0]["score"]), 4)
        )

    with col3:
        st.metric(
            "Ranked Profiles",
            "100,000"
        )

    st.divider()

    top_candidate = df.iloc[0]

    st.subheader("🏆 Highest Ranked Candidate")

    st.write(
        f"""
**Candidate ID:** {top_candidate['candidate_id']}

**Rank:** {top_candidate['rank']}

**Score:** {top_candidate['score']}
"""
    )

    if "reasoning" in df.columns:
        st.write("**Reasoning:**")
        st.info(top_candidate["reasoning"])

    st.divider()

    st.subheader("📊 Top 20 Ranked Candidates")

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("📥 Download Results")

    st.download_button(
        label="Download Submission CSV",
        data=df.to_csv(index=False),
        file_name="submission.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Could not load outputs/submission.csv\n\n{e}")

st.divider()

st.caption(
    "Built by Tanvi Nakum | Redrob Intelligent Candidate Discovery & Ranking Challenge"
)