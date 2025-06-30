import requests
import json
import pandas as pd
import os
from datetime import datetime

# === User-friendly script to extract JHU course data for multiple terms ===
# Output: CSV files in ../data/ for each term and a combined all_courses.csv

# === Constants for extraction ===
URL = "https://tn0vi78cyja5u3rgp.a1.typesense.net/multi_search"
API_KEY = "ck8wVFJjVFRWays5SGlpK3J0SmErQUpoOFdiVE11d3ozbTJRRWx5T3Riaz13N0RaeyJleGNsdWRlX2ZpZWxkcyI6IlNlY3Rpb25EZXRhaWxzLk1lZXRpbmdzLkxvY2F0aW9uLFNlY3Rpb25EZXRhaWxzLk1lZXRpbmdzLlJvb20ifQ=="
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'content-type': 'text/plain',
    'origin': 'https://courses.jhu.edu',
    'referer': 'https://courses.jhu.edu/',
    'user-agent': 'Mozilla/5.0',
}

def generate_terms(start_year=2019, end_year=None):
    """Generate a list of terms from Fall 2019 to the current year."""
    if end_year is None:
        end_year = datetime.now().year
    terms = []
    for year in range(start_year, end_year + 1):
        terms.append(f"Intersession {year}")
        terms.append(f"Spring {year}")
        terms.append(f"Summer {year}")
        terms.append(f"Fall {year}")
    return terms

def get_academic_year(term):
    parts = term.split()
    if len(parts) != 2:
        return ''
    season, year = parts
    year = int(year)
    if season.lower() == 'fall':
        return f"{str(year)[-2:]}-{str(year+1)[-2:]}"
    elif season.lower() == 'spring':
        return f"{str(year-1)[-2:]}-{str(year)[-2:]}"
    else:
        return ''

def get_all_courses(term, page=1):
    params = {"x-typesense-api-key": API_KEY}
    data = json.dumps({
        "searches": [{
            "query_by": "Title,OfferingName,OfferingVariations,SectionName,Description,InstructorsFullName",
            "infix": "always,off,off,off,off,off",
            "per_page": 30,
            "num_typos": "2,0,0,0,0,2",
            "exhaustive_search": True,
            "sort_by": "_text_match:desc,OfferingName:asc,SectionName:asc",
            "facet_return_parent": "Areas.Description",
            "highlight_full_fields": "Title,OfferingName,OfferingVariations,SectionName,Description,InstructorsFullName",
            "collection": "sections",
            "facet_by": "Areas.Description,SubDepartment,CNM_TermsID,SchoolName,AllDepartments,Level,LocationDelimited,Status,Credits,TimeOfDay",
            "filter_by": f"HierarchicalTerm.Value:=['{term}']",
            "max_facet_values": 100,
            "q": "",
            "page": page
        }]
    })
    response = requests.post(URL, params=params, headers=HEADERS, data=data)
    response.raise_for_status()
    return response.json()

def scrape_all_pages(term, max_pages=1000):
    all_courses = []
    academic_year = get_academic_year(term)
    for page in range(1, max_pages + 1):
        try:
            res = get_all_courses(term, page=page)
        except Exception as e:
            print(f"Error fetching page {page} for {term}: {e}")
            break
        sections = res.get("results", [{}])[0].get("hits", [])
        if not sections:
            break
        for s in sections:
            doc = s.get("document", {})
            all_courses.append({
                "Semester": term,
                "Academic Year": academic_year,
                "Location": doc.get("LocationDelimited"),
                "Course Name": doc.get("SectionName"),
                "Course Description": doc.get("Description"),
                "Department": doc.get("AllDepartments"),
                "School": doc.get("SchoolName"),
                "Credits": doc.get("Credits"),
                "Status": doc.get("Status"),
            })
    return pd.DataFrame(all_courses)

def initial_extraction(start_year=2019, end_year=None, max_pages=1000, outdir="./data"):
    """
    Download and save ALL semesters (overwriting existing files), and only if they have >300 classes.
    Returns a list of semesters added.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.abspath(os.path.join(script_dir, '..', 'data'))
    print(f"[DEBUG] Writing extracted data to: {outdir}")
    os.makedirs(outdir, exist_ok=True)
    terms = generate_terms(start_year, end_year)
    added_terms = []
    all_data = []
    for term in terms:
        print(f"Scraping {term}...")
        df = scrape_all_pages(term, max_pages=max_pages)
        if not df.empty and len(df) > 300:
            df.to_csv(os.path.join(outdir, f"{term.replace(' ', '_')}.csv"), index=False)
            all_data.append(df)
            added_terms.append(term)
    if all_data:
        df_all = pd.concat(all_data, ignore_index=True)
        df_all.to_csv(os.path.join(outdir, "all_courses.csv"), index=False)
    return added_terms

def incremental_scrape(start_year=2019, end_year=None, max_pages=1000, outdir="./data"):
    """
    Only download and save semesters not already present in the data directory, and only if they have >300 classes.
    Returns a list of new semesters added.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.abspath(os.path.join(script_dir, '..', 'data'))
    print(f"[DEBUG] Writing extracted data to: {outdir}")
    os.makedirs(outdir, exist_ok=True)
    terms = generate_terms(start_year, end_year)
    existing = set(f.replace('.csv','').replace('_',' ') for f in os.listdir(outdir) if f.endswith('.csv') and f != 'all_courses.csv')
    new_data = []
    new_terms = []
    for term in terms:
        if term.replace(' ', '_') in existing or term in existing:
            continue
        print(f"Scraping {term}...")
        df = scrape_all_pages(term, max_pages=max_pages)
        if not df.empty and len(df) > 300:
            df.to_csv(os.path.join(outdir, f"{term.replace(' ', '_')}.csv"), index=False)
            new_data.append(df)
            new_terms.append(term)
    # Update all_courses.csv
    all_csvs = [os.path.join(outdir, f) for f in os.listdir(outdir) if f.endswith('.csv') and f != 'all_courses.csv']
    if all_csvs:
        df_all = pd.concat([pd.read_csv(f) for f in all_csvs], ignore_index=True)
        df_all.to_csv(os.path.join(outdir, "all_courses.csv"), index=False)
    return new_terms

if __name__ == "__main__":
    print("Starting initial extraction from Fall 2019...")
    added = initial_extraction()
    print(f"Added semesters: {added}")
    print("Now running incremental scrape...")
    added2 = incremental_scrape()
    print(f"Added new semesters: {added2}")
    print("Extraction complete! Check the data folder for results.") 