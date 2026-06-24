import streamlit as st
import pandas as pd

st.title("Redrob AI Candidate Ranker")

st.write(
    "Demo version of the Intelligent Candidate Discovery & Ranking System"
)

uploaded_file = st.file_uploader(
    "Upload ranked_candidates.csv",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.success("File Loaded")

    st.dataframe(df.head(20))

    csv = df.to_csv(index=False)

    st.download_button(
        "Download CSV",
        csv,
        "submission.csv",
        "text/csv"
    )