# classification.py
"""
Classify courses into four groups based on keywords, semantic scores, or embedding similarity.

Categories:
1. Not Related
2. About Planetary Health
3. Planetary Health Core Concept
4. Planetary Health Adjacent

Edit the keyword lists below to match your taxonomy.
"""

import numpy as np
import pandas as pd
# For semantic similarity
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# === Detailed Keyword Lists by Tiers ===
tier1 = ["planetary health"]
tier2 = [
    "systems approach", "environmental change", "human health"
]
tier3 = [
    "sustainability", "environmental justice", "resilience", "air pollution", "urbanization",
    "greenhouse gases", "pollution", "chemical pollution", "climate change", "biodiversity loss",
    "ecosystem services", "resource scarcity", "ocean acidification", "land use change",
    "mental health", "public health", "disaster preparedness", "adaptation", "mitigation"
]

CATEGORY_LABELS = [
    "About Planetary Health",           # tier1
    "Planetary Health Core Concept",    # tier2
    "Planetary Health Adjacent",        # tier3
    "Not Related"                      # none
]

def label_course(text):
    """Rule-based classification into four groups based on keywords."""
    text = text.lower() if isinstance(text, str) else ""
    if any(kw in text for kw in tier1):
        return CATEGORY_LABELS[0]
    elif any(kw in text for kw in tier2):
        return CATEGORY_LABELS[1]
    elif any(kw in text for kw in tier3):
        return CATEGORY_LABELS[2]
    else:
        return CATEGORY_LABELS[3]

def batch_label_courses(texts):
    """Apply rule-based classification to a pandas Series or list of texts."""
    return [label_course(t) for t in texts]

# --- Semantic Similarity Classification ---
def semantic_similarity_classify(df, known_examples, model_name="all-MiniLM-L6-v2", text_col="full_text"):
    """
    Classify courses by semantic similarity to known planetary health examples.
    - df: DataFrame with a column text_col
    - known_examples: list of prototypical planetary health course descriptions
    - model_name: SentenceTransformer model name
    - text_col: column to use for course text
    Returns: DataFrame with a new column 'semantic_score'
    """
    model = SentenceTransformer(model_name)
    known_embeddings = model.encode(known_examples, convert_to_tensor=True)
    catalog_embeddings = model.encode(df[text_col].tolist(), convert_to_tensor=True)
    similarities = cosine_similarity(catalog_embeddings.cpu().numpy(), known_embeddings.cpu().numpy())
    df['semantic_score'] = similarities.max(axis=1)
    return df

# --- Zero-shot Classification (HuggingFace Transformers) ---
def zero_shot_classify(texts, candidate_labels=None, model_name="facebook/bart-large-mnli"):
    """
    Classify texts using zero-shot classification. Requires transformers library.
    - texts: list of strings
    - candidate_labels: list of category names or descriptions
    Returns: list of predicted labels
    """
    try:
        from transformers import pipeline
    except ImportError:
        raise ImportError("transformers library is required for zero-shot classification.")
    if candidate_labels is None:
        candidate_labels = CATEGORY_LABELS
    classifier = pipeline("zero-shot-classification", model=model_name)
    results = classifier(texts, candidate_labels)
    # Return the label with the highest score for each text
    return [r['labels'][0] for r in results]

# --- Clustering-based Classification (Exploratory) ---
def cluster_courses(df, model_name="all-MiniLM-L6-v2", text_col="full_text", n_clusters=4):
    """
    Cluster courses using embeddings and KMeans. Returns cluster labels.
    - df: DataFrame with a column text_col
    - model_name: SentenceTransformer model name
    - n_clusters: number of clusters
    Returns: DataFrame with a new column 'cluster_label'
    """
    from sklearn.cluster import KMeans
    model = SentenceTransformer(model_name)
    embeddings = model.encode(df[text_col].tolist(), convert_to_tensor=True)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings.cpu().numpy())
    df['cluster_label'] = cluster_labels
    return df

if __name__ == "__main__":
    # Example usage
    # Load your data
    # df = pd.read_json("fa25.json")
    # df["full_text"] = df["Course Name"] + " " + df["Course Description"]
    # Rule-based
    # df["PH_Label"] = df["full_text"].apply(label_course)
    # print(df["PH_Label"].value_counts())
    # Semantic similarity
    # known_examples = [ ... ]  # List of planetary health course descriptions
    # df = semantic_similarity_classify(df, known_examples)
    # print(df.sort_values("semantic_score", ascending=False).head(10))
    # Zero-shot
    # labels = zero_shot_classify(df["full_text"].tolist())
    # print(labels[:10])
    # Clustering
    # df = cluster_courses(df)
    # print(df["cluster_label"].value_counts())
    print("Classification module ready. See __main__ for usage examples.") 