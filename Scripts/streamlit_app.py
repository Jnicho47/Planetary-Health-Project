import streamlit as st
import pandas as pd
import os
import sys
import socket

# Ensure the Scripts directory is in sys.path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if script_dir not in sys.path:
    sys.path.append(script_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from Scripts.classification import (
    label_course, semantic_similarity_classify, zero_shot_classify, cluster_courses
)
from Scripts.extract_all_terms import incremental_scrape

def get_available_semesters(data_dir):
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and f != 'all_courses.csv']
    return sorted([f.replace('.csv', '').replace('_', ' ') for f in files])

def load_semester_data(data_dir, selected):
    dfs = []
    for sem in selected:
        fname = os.path.join(data_dir, sem.replace(' ', '_') + '.csv')
        if os.path.exists(fname):
            dfs.append(pd.read_csv(fname))
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def keyword_analysis(df, env_keywords, health_keywords):
    env_keywords = [k.lower() for k in env_keywords]
    health_keywords = [k.lower() for k in health_keywords]
    def label_row(row):
        text = (str(row.get('Course Name', '')) + ' ' + str(row.get('Course Description', ''))).lower()
        if 'planetary health' in text:
            return 'Category 1: Explicitly Planetary Health'
        if 'systems' in text and any(k in text for k in env_keywords) and any(k in text for k in health_keywords):
            return 'Category 2: Planetary Health Concept'
        if any(k in text for k in env_keywords) or any(k in text for k in health_keywords):
            return 'Category 3: Related Concept'
        return 'Not Related'
    df['PH_Label'] = df.apply(label_row, axis=1)
    return df

def check_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

# --- UI Layout ---
st.set_page_config(page_title="JHU Planetary Health Course Analysis", layout="wide")

st.markdown("""
# 🌎 JHU Planetary Health Course Analysis

Welcome! This tool lets you fetch, analyze, and classify JHU course data for planetary health research—**no coding required**.

**How it works:**
1. Click **Update Course Data** to fetch the latest semesters (only new ones with >300 classes are added).
2. Select semesters/academic years to analyze.
3. Adjust keywords for environmental change and human health.
4. Click **Run Keyword Analysis** to classify and download results.

---
""")

# --- Data Directory ---
data_dir = os.path.join(project_root, 'data')
os.makedirs(data_dir, exist_ok=True)

# --- Scraping Button and Feedback ---
col1, col2 = st.columns([1, 3])
with col1:
    scrape_btn = st.button("🔄 Update Course Data from JHU Catalog")
with col2:
    st.markdown("**This may take a few minutes. Only new semesters will be added.**")

scrape_status = st.empty()

if scrape_btn:
    if not check_internet():
        scrape_status.error("No internet connection. Please check your network and try again.")
    else:
        with scrape_status, st.spinner("Extracting latest course data from JHU. Please wait..."):
            try:
                new_terms = incremental_scrape()
                if new_terms:
                    st.success(f"✅ Added new semesters: {', '.join(new_terms)}")
                else:
                    st.info("No new semesters found. All available data is up to date.")
            except Exception as e:
                st.error(f"❌ Error updating course data: {e}")
                st.markdown("""
                **Troubleshooting:**
                - Check your internet connection.
                - The JHU course catalog may be temporarily unavailable.
                - If the problem persists, contact your technical support team.
                """)

semesters = get_available_semesters(data_dir)
if not semesters:
    st.warning("No course data found. Click 'Update Course Data from JHU Catalog' above to fetch the latest data.")
    st.stop()

# --- Semester Selection and Keyword Analysis ---
st.markdown("---")
st.header("Analyze Courses by Semester and Keywords")

selected_semesters = st.multiselect(
    "Select semesters/academic years to analyze:",
    semesters,
    default=semesters[-1:]  # Default to most recent
)

def_list_env = [
    "environmental change", "air pollution", "biodiversity loss", "climate change", "resource scarcity",
    "land use change", "nutrient cycling", "ocean degradation", "environment", "eco-systems"
]
def_list_health = [
    "human health", "infectious diseases", "injuries", "reproductive health", "mental health",
    "noncommunicable diseases", "nutritional diseases", "displacement", "conflict", "mortality"
]

with st.expander("Adjust Keyword Lists (optional)"):
    env_keywords = st.text_area(
        "Environmental change keywords (comma-separated)",
        value=", ".join(def_list_env),
        height=60
    ).split(",")
    health_keywords = st.text_area(
        "Human health keywords (comma-separated)",
        value=", ".join(def_list_health),
        height=60
    ).split(",")
    env_keywords = [k.strip() for k in env_keywords if k.strip()]
    health_keywords = [k.strip() for k in health_keywords if k.strip()]

run_analysis = st.button("🚦 Run Keyword Analysis")

if run_analysis:
    df = load_semester_data(data_dir, selected_semesters)
    if df.empty:
        st.warning("No data found for selected semesters. Try updating the course data or selecting different semesters.")
    else:
        df = keyword_analysis(df, env_keywords, health_keywords)
        st.success(f"Analysis complete! {len(df)} courses analyzed.")
        st.write(df["PH_Label"].value_counts())
        st.dataframe(df[["Course Name", "PH_Label", "Semester", "Academic Year"] + [c for c in df.columns if c not in ["Course Name", "PH_Label", "Semester", "Academic Year"]]].head(50))
        st.download_button("⬇️ Download Results as CSV", df.to_csv(index=False), "keyword_analysis_results.csv")

# --- Troubleshooting Section ---
st.markdown("""
---
### Troubleshooting
- If no data appears after scraping, check your internet connection and try again.
- If the JHU catalog is down or slow, wait a few minutes and retry.
- For persistent issues, contact your technical support team or check the API status.
""")

# Load the latest data if available
all_courses_path = os.path.join(data_dir, 'all_courses.csv')
if os.path.exists(all_courses_path):
    df = pd.read_csv(all_courses_path)
    st.write("Data Preview:", df.head())

    method = st.selectbox(
        "Choose classification method",
        ["Rule-based", "Semantic Similarity", "Zero-shot", "Clustering"]
    )

    if method == "Rule-based":
        st.markdown("Rule-based: Uses keyword matching to assign categories.")
        if "full_text" in df.columns:
            df["PH_Label"] = df["full_text"].apply(label_course)
        elif "Course Name" in df.columns and "Course Description" in df.columns:
            df["full_text"] = df["Course Name"].astype(str) + " " + df["Course Description"].astype(str)
            df["PH_Label"] = df["full_text"].apply(label_course)
        else:
            st.error("Input data must have 'Course Name' and 'Course Description' columns or a 'full_text' column.")
            st.stop()
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