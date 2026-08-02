"""
language_detector.py

Detects whether a query is pure English, native-script Telugu,
or Romanized code-mixed Telugu-English (e.g. "AI jobs Hyderabad lo unnaya").

Off-the-shelf langdetect is unreliable on short, noisy, romanized
code-mixed text (this is a known problem highlighted in code-mixed
NLP literature -- romanized Indic text has no standard script cues
for statistical language ID to latch onto). So we use a lightweight
rule-based layer on top of langdetect:

1. If the text contains native Telugu unicode characters -> "te"
2. Else check for common romanized Telugu function words
   (postpositions, verb endings, pronouns) -> "code-mixed"
3. Else fall back to langdetect -> "en" / other
"""

from langdetect import detect, LangDetectException

# Common romanized Telugu function words / verb endings that show up
# in code-mixed queries regardless of the English content mixed in.
# This list is intentionally small and high-precision (function words
# rather than content words) to minimize false positives on English text.
TELUGU_MARKERS = {
    "unnaya", "unnayi", "undi", "ledu", "kavali", "chestunna",
    "chesta", "chey", "cheyali", "enti", "ento", "meeru", "nenu",
    "vaadu", "vaallu", "manam", "naaku", "neeku", "vaariki",
    "lo", "ki", "nunchi", "tho", "ga", "ante", "kosam", "vundi",
    "emi", "ela", "eppudu", "akkada", "ikkada", "bాగుంది", "bagundi",
    "chala", "koncham", "inka", "malli", "ippudu", "raa", "raandi",
    "cheppu", "chudandi", "vellali", "vachindi", "ok"
}


def _contains_telugu_script(text: str) -> bool:
    return any("\u0C00" <= ch <= "\u0C7F" for ch in text)


def _contains_telugu_markers(text: str) -> bool:
    words = set(text.lower().split())
    return len(words & TELUGU_MARKERS) > 0


def detect_language(text: str) -> str:
    """
    Returns one of: "te" (native script Telugu), "code-mixed"
    (romanized Telugu-English), "en" (English), or the langdetect
    ISO code as a fallback for anything else.
    """

    if not text or not text.strip():
        return "unknown"

    if _contains_telugu_script(text):
        return "te"

    if _contains_telugu_markers(text):
        return "code-mixed"

    try:
        lang = detect(text)
    except LangDetectException:
        return "unknown"

    return lang


def is_code_mixed(text: str) -> bool:
    return detect_language(text) == "code-mixed"
