"""
codemix.py

Handles code-mixed (Telugu-English) query processing for the RAG
pipeline in two ways:

1. expand_query() - the original keyword-expansion approach (kept
   as-is for backward compatibility with test_codemix.py / anything
   else already calling it).

2. normalize_for_alignment() - a new function inspired by the
   ContrastiveMix paper's finding that code-mixed QUERY embeddings
   align better with target-language content once function words /
   noisy transliteration are stripped out, leaving the semantic core
   in English. ContrastiveMix does this alignment through an extra
   contrastive loss during training; we don't have the infra to train
   a custom encoder, so we approximate the same idea at inference
   time by generating a "cleaned" variant of the query and averaging
   its embedding with the original query's embedding before search.
   This is a lightweight, explainable stand-in for the paper's idea
   and is the main "novelty" angle of this project.
"""

from backend.language_detector import TELUGU_MARKERS

# Kept from the original implementation.
DOMAIN_SYNONYMS = {
    "ai": ["artificial intelligence", "machine learning"],
    "jobs": ["employment", "career"],
    "rag": ["retrieval augmented generation"]
}


def expand_query(query):

    expanded = [query]

    words = query.lower().split()

    extra = []

    for word in words:
        if word in DOMAIN_SYNONYMS:
            extra.extend(DOMAIN_SYNONYMS[word])

    if extra:
        expanded.append(query + " " + " ".join(extra))

    return expanded


def normalize_for_alignment(query: str) -> str:
    """
    Strips romanized Telugu function words / postpositions out of a
    code-mixed query, leaving behind the English content words that
    carry the actual search intent.

    "AI jobs Hyderabad lo unnaya" -> "AI jobs Hyderabad"

    If nothing is stripped (i.e. the query has no Telugu markers),
    the original query is returned unchanged -- this keeps pure
    English queries from being altered at all.
    """

    words = query.split()

    cleaned = [w for w in words if w.lower() not in TELUGU_MARKERS]

    cleaned_query = " ".join(cleaned).strip()

    if not cleaned_query:
        return query

    return cleaned_query
