import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(__file__))
from classification import label_course
from analysis import plot_yearly_trends, plot_departmental_breakdown

st.set_page_config(page_title="JHU Planetary Health Course Analysis", layout="wide")
st.title("JHU Planetary Health Course Analysis")

st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Upload your course data CSV (from the data folder).
2. The app will classify courses and show results.
3. Download the classified data as CSV.
4. View visualizations of trends and department breakdowns.
""")

uploaded = st.file_uploader("Upload course data CSV", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)
    # Use 'Course Description' or 'full_text' for classification
    if 'full_text' in df.columns:
        text_col = 'full_text'
    elif 'Course Description' in df.columns:
        text_col = 'Course Description'
    else:
        st.error("No suitable text column found for classification.")
        st.stop()

    # Apply rule-based classification
    df["PH_Label"] = df[text_col].apply(label_course)
    st.write("### Data Preview", df.head())
    st.write("### Classification Counts", df["PH_Label"].value_counts())

    # Download results
    st.download_button("Download Results as CSV", df.to_csv(index=False), "classified_courses.csv")

    # Visualizations
    st.write("### Yearly Trends")
    plot_yearly_trends(df)
    st.write("### Departmental Breakdown")
    plot_departmental_breakdown(df) 