import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Redrob AI Candidate Ranker",
    layout="wide"
)

st.title("Redrob AI Candidate Ranker")

st.markdown("""
### Intelligent Candidate Discovery & Ranking System

The ranking engine evaluates candidates using:

- AI/ML title relevance
- Retrieval, ranking, and recommendation system experience
- Production ML and data engineering evidence
- Skill strength, endorsements, and assessments
- Experience fit for the target role
- Behavioral hiring signals
- Location and relocation fit
- Honeypot and profile consistency checks

The final ranking is generated using a deterministic CPU-only scoring pipeline with no external API calls during ranking.
""")

try:
    df = pd.read_csv("outputs/submission.csv")

    st.success("Top 100 candidate ranking loaded successfully")

    # Metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidates Ranked", len(df))

    with col2:
        st.metric("Top Score", round(df["score"].max(), 4))

    with col3:
        st.metric("Lowest Score", round(df["score"].min(), 4))

    st.divider()

    # Table
    st.subheader("Top 100 Ranked Candidates")

    sst.dataframe(
    df.head(100),
    height=700,
    width="stretch",
    hide_index=True,
    column_config={
        "candidate_id": st.column_config.TextColumn(
            "Candidate ID",
            width="small"      # was medium
        ),
        "rank": st.column_config.NumberColumn(
            "Rank",
            width="small"
        ),
        "score": st.column_config.NumberColumn(
            "Score",
            format="%.4f",
            width="small"
        ),
        "reasoning": st.column_config.TextColumn(
            "Reasoning",
            width="large"
        )
        }
    )

    st.divider()

    # Reasoning Explorer
    st.subheader("Candidate Reasoning Explorer")

    selected_rank = st.selectbox(
        "Select Candidate Rank",
        df["rank"].tolist()
    )

    candidate = df[df["rank"] == selected_rank].iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Rank", int(candidate["rank"]))

    with col2:
        st.metric("Score", float(candidate["score"]))

    st.text_area(
        "Full Reasoning",
        candidate["reasoning"],
        height=150
    )

    st.divider()

    st.download_button(
        label="📥 Download Submission CSV",
        data=df.to_csv(index=False),
        file_name="submission.csv",
        mime="text/csv"
    )

except FileNotFoundError:
    st.error(
        "outputs/submission.csv not found. Run 'python main.py' first."
    )

except Exception as e:
    st.error(f"Error loading submission file: {e}")