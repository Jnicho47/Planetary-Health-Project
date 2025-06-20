# analysis.py
"""
Analysis functions for Planetary Health course data.
Includes yearly trends, departmental breakdown, taxonomy coverage, and enrollment analysis.
"""
import pandas as pd
import matplotlib.pyplot as plt

def plot_yearly_trends(df, label_col="PH_Label"):
    """Plot stacked bar chart of course counts by year and label."""
    df["Year"] = df["Term"].str.extract(r'(\d{4})')
    yearly = df.groupby(["Year", label_col]).size().unstack(fill_value=0)
    ax = yearly.plot(kind="bar", stacked=True, figsize=(12,6), title="Planetary Health Course Trends by Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Courses")
    plt.tight_layout()
    plt.show()

def plot_departmental_breakdown(df, label_col="PH_Label"):
    """Plot horizontal stacked bar chart of course counts by department and label."""
    dept = df.groupby(["Department", label_col]).size().unstack(fill_value=0)
    dept = dept[dept.sum(axis=1) > 0]  # filter depts with at least one match
    ax = dept.plot(kind="barh", stacked=True, figsize=(10,20), title="Departmental Distribution")
    plt.xlabel("Number of Courses")
    plt.ylabel("Department")
    plt.tight_layout()
    plt.show()

def taxonomy_coverage(df, taxonomy_keywords):
    """Return a Series with counts of courses covering each taxonomy category."""
    coverage = {}
    for cat, kws in taxonomy_keywords.items():
        coverage[cat] = df["full_text"].apply(lambda x: any(kw in str(x).lower() for kw in kws)).sum()
    return pd.Series(coverage)

def enrollment_analysis(df):
    """Placeholder for enrollment analysis (implement if enrollment data is available)."""
    if 'Enrollment' in df.columns:
        return df.groupby('Year')['Enrollment'].sum()
    else:
        print("No enrollment data available.")
        return None

if __name__ == "__main__":
    # Example usage for non-coders
    data = {
        'Term': ['Fall 2024', 'Spring 2025'],
        'Department': ['Public Health', 'Biology'],
        'PH_Label': ['About Planetary Health', 'Planetary Health Core Concept'],
        'full_text': ['planetary health and climate change', 'biodiversity and sustainability']
    }
    df = pd.DataFrame(data)
    plot_yearly_trends(df)
    plot_departmental_breakdown(df) 