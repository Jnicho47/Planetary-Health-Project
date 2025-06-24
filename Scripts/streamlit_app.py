import streamlit as st
import pandas as pd
import os
from Scripts.classification import (
    label_course, semantic_similarity_classify, zero_shot_classify, cluster_courses
)
from Scripts.extract_all_terms import scrape_all_years

st.set_page_config(page_title="JHU Planetary Health Course Analysis", layout="wide")
st.title("JHU Planetary Health Course Analysis")

st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload your course data CSV (from the data folder).
2. The app will classify courses and show results.
3. Download the classified data as CSV.
4. View visualizations of trends and department breakdowns.
""")

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
all_courses_path = os.path.join(data_dir, 'all_courses.csv')

if st.button("Update Course Data from JHU Catalog"):
    with st.spinner("Extracting latest course data. This may take a few minutes..."):
        try:
            scrape_all_years()
            st.success("Course data updated successfully!")
        except Exception as e:
            st.error(f"Error updating course data: {e}")

# Load the latest data if available
if os.path.exists(all_courses_path):
    df = pd.read_csv(all_courses_path)
    st.write("Data Preview:", df.head())

    method = st.selectbox(
        "Choose classification method",
        ["Rule-based", "Semantic Similarity", "Zero-shot", "Clustering"]
    )

    if method == "Rule-based":
        st.markdown("Rule-based: Uses keyword matching to assign categories.")
        df["PH_Label"] = df["full_text"].apply(label_course) if "full_text" in df.columns else df["Course Name"].astype(str) + " " + df["Course Description"].astype(str).apply(label_course)
        st.write(df["PH_Label"].value_counts())
    elif method == "Semantic Similarity":
        st.markdown("Semantic Similarity: Compares your courses to known planetary health examples using AI.")
        examples = st.text_area(
            "Enter known planetary health course examples (one per line)",
            height=150
        )
        known_examples = [e.strip() for e in examples.splitlines() if e.strip()]
        if st.button("Run Semantic Similarity"):
            if not known_examples:
                st.error("Please provide at least one known example.")
            else:
                with st.spinner("Running semantic similarity classification..."):
                    df = semantic_similarity_classify(df, known_examples)
                st.write(df.sort_values("semantic_score", ascending=False).head(10))
                st.write(df["semantic_score"].describe())
    elif method == "Zero-shot":
        st.markdown("Zero-shot: Uses a language model to assign categories based on your label descriptions.")
        candidate_labels = st.text_input(
            "Enter candidate labels (comma-separated)",
            value="About Planetary Health,Planetary Health Core Concept,Planetary Health Adjacent,Not Related"
        )
        if st.button("Run Zero-shot Classification"):
            with st.spinner("Running zero-shot classification (this may take a while)..."):
                labels = zero_shot_classify(df["full_text"].tolist(), [l.strip() for l in candidate_labels.split(",")])
                df["PH_Label"] = labels
            st.write(df["PH_Label"].value_counts())
    elif method == "Clustering":
        st.markdown("Clustering: Groups courses into clusters using AI embeddings.")
        n_clusters = st.number_input("Number of clusters", min_value=2, max_value=10, value=4)
        if st.button("Run Clustering"):
            with st.spinner("Running clustering (this may take a while)..."):
                df = cluster_courses(df, n_clusters=int(n_clusters))
            st.write(df["cluster_label"].value_counts())

    st.markdown("---")
    st.download_button("Download Results as CSV", df.to_csv(index=False), "classified_courses.csv")
    st.write("Preview of classified data:", df.head())

    # Visualizations
    st.write("### Yearly Trends")
    plot_yearly_trends(df)
    st.write("### Departmental Breakdown")
    plot_departmental_breakdown(df)
else:
    st.info("No course data found. Click the button above to fetch the latest data.") 