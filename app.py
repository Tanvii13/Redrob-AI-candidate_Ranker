import json

import pandas as pd
import streamlit as st

from main import score_candidate, honeypot_penalty, reasoning, load_job_text

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

The final ranking is generated using a deterministic CPU-only scoring pipeline
with no external API calls during ranking.
""")

MAX_SANDBOX_CANDIDATES = 100  

tab_live, tab_precomputed = st.tabs(
    ["🔬 Live Sandbox (upload & rank)", "📊 Full Submission (pre-computed top 100)"]
)

with tab_live:
    st.subheader("Upload a candidate sample")
    st.caption(
        "Upload a .json (array of candidate objects) or .jsonl (one JSON object "
        "per line) file. Per challenge rules, the sandbox is for small samples "
        f"only — at most {MAX_SANDBOX_CANDIDATES} candidates will be scored here."
    )

    uploaded_file = st.file_uploader(
        "Candidate file",
        type=["json", "jsonl"],
        key="candidate_uploader",
    )

    def parse_uploaded_file(file):
        """Returns a list of candidate dicts from an uploaded .json or .jsonl file."""
        raw = file.read().decode("utf-8")
        if file.name.endswith(".jsonl"):
            return [json.loads(line) for line in raw.splitlines() if line.strip()]
        data = json.loads(raw)
        if isinstance(data, dict):
            return [data]
        return data

    if uploaded_file is not None:
        try:
            candidates = parse_uploaded_file(uploaded_file)
        except Exception as exc:
            st.error(f"Could not parse the uploaded file: {exc}")
            candidates = []

        if candidates:
            if len(candidates) > MAX_SANDBOX_CANDIDATES:
                st.warning(
                    f"File has {len(candidates)} candidates. The sandbox only "
                    f"scores the first {MAX_SANDBOX_CANDIDATES} to stay within "
                    "the small-sample sandbox rule (Section 10.5)."
                )
                candidates = candidates[:MAX_SANDBOX_CANDIDATES]

            with st.spinner(f"Scoring {len(candidates)} candidate(s)..."):
                rows = []
                honeypot_rows = []
                for candidate in candidates:
                    try:
                        scored = score_candidate(candidate)
                        scored["reasoning"] = reasoning(candidate, scored)
                        rows.append(scored)
                        if scored["penalty"] > 0:
                            honeypot_rows.append(scored)
                    except Exception as exc:
                        st.warning(
                            f"Skipped a candidate due to an error: {exc}"
                        )

            if not rows:
                st.error("No candidates could be scored from this file.")
            else:
                rows.sort(key=lambda r: (-r["score"], r["candidate_id"]))
                result_df = pd.DataFrame(rows)

                st.success(f"Scored {len(rows)} candidate(s) successfully.")

                st.divider()
                st.subheader("How many candidates to view?")

                view_choice = st.radio(
                    "View top:",
                    ["Top 10", "Top 50", "Top 100", "Custom"],
                    horizontal=True,
                    key="view_choice",
                )

                if view_choice == "Custom":
                    n = st.number_input(
                        "Enter number of candidates to view",
                        min_value=1,
                        max_value=len(result_df),
                        value=min(20, len(result_df)),
                    )
                else:
                    requested = int(view_choice.split()[-1])
                    n = min(requested, len(result_df))

                st.dataframe(
                    result_df.head(int(n))[
                        [
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
                            "reasoning",
                        ]
                    ],
                    hide_index=True,
                    width="stretch",
                )

                st.divider()
                st.subheader("🚩 Flagged Honeypot / Suspicious Candidates")
                st.caption(
                    "Candidates with a non-zero consistency penalty — likely "
                    "keyword-stuffed skills, implausible experience timelines, "
                    "or other profile inconsistencies."
                )

                if honeypot_rows:
                    honeypot_df = pd.DataFrame(honeypot_rows).sort_values(
                        "penalty", ascending=False
                    )
                    st.write(f"{len(honeypot_rows)} flagged out of {len(rows)} scored.")
                    st.dataframe(
                        honeypot_df[
                            ["candidate_id", "name", "score", "penalty", "reasoning"]
                        ],
                        hide_index=True,
                        width="stretch",
                    )
                else:
                    st.write("No honeypot/consistency issues detected in this sample.")

                st.divider()
                st.download_button(
                    label="📥 Download scored results (CSV)",
                    data=result_df.to_csv(index=False),
                    file_name="sandbox_scored_results.csv",
                    mime="text/csv",
                )
    else:
        st.info(
            "No file uploaded yet. Try data/sample_candidates.json from the "
            "challenge bundle to test the sandbox."
        )

with tab_precomputed:
    try:
        df = pd.read_csv("outputs/submission.csv")

        st.success("Top 100 candidate ranking loaded successfully")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Candidates Ranked", len(df))
        with col2:
            st.metric("Top Score", round(df["score"].max(), 4))
        with col3:
            st.metric("Lowest Score", round(df["score"].min(), 4))

        st.divider()
        st.subheader("Top 100 Ranked Candidates")

        st.dataframe(
            df.head(100),
            height=700,
            width="stretch",
            hide_index=True,
            column_config={
                "candidate_id": st.column_config.TextColumn("CANDIDATE ID", width="small"),
                "rank": st.column_config.NumberColumn("Rank", width="small"),
                "score": st.column_config.NumberColumn("Score", format="%.4f", width="small"),
                "reasoning": st.column_config.TextColumn("Reasoning", width="large"),
            },
        )
        st.divider()

        st.subheader("Candidate Reasoning Explorer")
        selected_rank = st.selectbox("Select Candidate Rank", df["rank"].tolist())
        candidate = df[df["rank"] == selected_rank].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rank", int(candidate["rank"]))
        with col2:
            st.metric("Score", float(candidate["score"]))

        st.text_area("Full Reasoning", candidate["reasoning"], height=150)

        st.divider()
        st.download_button(
            label="📥 Download Submission CSV",
            data=df.to_csv(index=False),
            file_name="submission.csv",
            mime="text/csv",
        )

    except FileNotFoundError:
        st.error("outputs/submission.csv not found. Run 'python main.py' first.")
    except Exception as e:
        st.error(f"Error loading submission file: {e}")
