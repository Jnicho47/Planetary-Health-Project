# JHU Planetary Health Course Analysis

This project provides tools to extract, classify, and analyze Johns Hopkins University course data for Planetary Health content. It includes scripts for data extraction, classification, analysis, and a user-friendly Streamlit web app.

## Features
- Extract course data for multiple semesters/years
- Classify courses into four groups: Not Related, About Planetary Health, Planetary Health Core Concept, Planetary Health Adjacent
- Analyze trends, departmental breakdowns, and taxonomy coverage
- Visualize results and export to CSV
- Easy-to-use web interface (Streamlit)

## Setup
1. **Clone or download this repository.**
2. **Install dependencies:**
   ```bash
   pip install pandas matplotlib streamlit
   ```
3. **(Optional) Add or update keyword lists in `classification.py` for your taxonomy.**

## Data Extraction
- Use your extraction script (e.g., `extract_all_terms.py`) to download course data for all terms/years.
- The script will save CSV files in the `all_terms_data` folder.

## Classification
- The `classification.py` module provides rule-based and semantic classification functions.
- You can use these functions in your own scripts or through the Streamlit app.

## Analysis
- The `analysis.py` module provides functions for:
  - Yearly/semesterly trends
  - Departmental breakdowns
  - Taxonomy coverage
  - (Optional) Enrollment analysis

## Streamlit Web App
1. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```
2. **Upload your course data CSV.**
3. **View classification results, download CSV, and explore visualizations.**

## Usage Example
- Extract data:
  ```bash
  python extract_all_terms.py
  ```
- Run the web app:
  ```bash
  streamlit run streamlit_app.py
  ```
- Upload a CSV (e.g., `all_terms_data/all_courses.csv`), view results, and download classified data.

## Customization
- Update keyword lists in `classification.py` to match your taxonomy.
- Add new analysis or visualization functions in `analysis.py` as needed.

## License
MIT License 