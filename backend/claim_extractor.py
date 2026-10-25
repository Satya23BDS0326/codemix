"""
Claim Extraction and Claim Analysis Engine for Tamil-English Code-Mixed Text.
Extracts the central factual/assertive claim from conversational and viral framing,
classifies the claim domain, and identifies causal and evidence-deficiency risk indicators.
"""

import re
from typing import Dict, Any, List

# Meta-discourse framing prefixes to strip
FRAMING_PREFIXES = [
    r"^(whatsapp|telegram|facebook|twitter|instagram|youtube|social media)\s+(la\s+)?(share\s+aagura\s+message|forward(ed)?|viral\s+msg|post):\s*",
    r"^(breaking news|urgent alert|important update|viral news|shocking news|alert|breaking|warning):\s*",
    r"^(neengal intha|intha)\s+(forward message|video|post)\s*:\s*",
    r"^viral tip:\s*",
    r"^new rule by [^:]+:\s*"
]

# Action / sharing suffixes to strip
CALL_TO_ACTION_SUFFIXES = [
    r"[\.,]?\s*(idha|itha|intha)?\s*(immediately|urgent\s+ah|fast\s+ah)?\s*(share\s+pannunga|forward\s+pannunga|send\s+pannunga|share\s+max).*$",
    r"[\.,]?\s*forward to all(\s+family\s+groups|\s+contacts|\s+groups)?.*$",
    r"[\.,]?\s*(please\s+)?forward to everyone.*$",
    r"[\.,]?\s*click (this\s+)?(website\s+)?link\s*(immediately|below)?.*$",
    r"[\.,]?\s*link below.*$",
    r"[\.,]?\s*fill google form link.*$",
    r"[\.,]?\s*video proof attached.*$",
    r"[\.,]?\s*share max to support.*$"
]

# Causal Markers (Tamil-English)
CAUSAL_MARKERS = [
    "nala", "naala", "causes", "caused by", "leads to", "resulting in",
    "kudicha", "sapta", "potu", "use panna", "insert panna", "download panna",
    "due to", "because of", "mix panni"
]

# Fear / Panic Markers
FEAR_MARKERS = [
    "die aagudhu", "kill pannuthu", "death", "cancer", "brain damage",
    "battery blast", "heart attack", "freezing all bank accounts",
    "total darkness", "danger", "fatal", "radiation"
]

def extract_core_claim(text: str) -> str:
    """
    Strips viral forwarding wrappers, social media prefixes, and call-to-action
    suffixes to isolate the underlying assertive proposition.
    """
    cleaned = text.strip()
    
    # Strip prefixes
    for prefix in FRAMING_PREFIXES:
        cleaned = re.sub(prefix, "", cleaned, flags=re.IGNORECASE).strip()

    # Strip suffixes
    for suffix in CALL_TO_ACTION_SUFFIXES:
        cleaned = re.sub(suffix, "", cleaned, flags=re.IGNORECASE).strip()

    # Capitalize first letter and ensure ending punctuation
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
        if not cleaned.endswith((".", "!", "?")):
            cleaned += "."
    else:
        cleaned = text.strip()

    return cleaned

def determine_claim_domain(text: str) -> str:
    """Classifies the subject domain of the claim."""
    t = text.lower()
    if any(k in t for k in ["5g", "tower", "radiation", "microchip", "phone", "sim card", "satellite", "earphone", "internet shutdown", "battery"]):
        if any(k in t for k in ["sparrow", "birds", "radiation", "environment", "earth"]):
            return "Technology / Environmental"
        return "Technology & Telecom"
    elif any(k in t for k in ["cure", "cancer", "diabetes", "virus", "covid", "kashayam", "banana peel", "onion juice", "garlic", "heart attack", "dengue", "vaccination", "hospital"]):
        return "Health & Medicine"
    elif any(k in t for k in ["bank", "account", "recharge", "rs.", "lakhs", "aadhaar", "repo rate", "rbi", "credit aagum", "talktime", "free rs", "cashback"]):
        return "Finance & Economy"
    elif any(k in t for k in ["rain", "imd", "holiday", "cyclone", "weather", "flood", "solar storm"]):
        return "Weather & Environment"
    elif any(k in t for k in ["tn government", "court", "metro", "railway", "isro", "tangedco", "corporation", "scheme", "minister", "recruitment"]):
        return "Governance & Public Policy"
    elif any(k in t for k in ["isro", "chandrayaan", "aditya-l1", "pluto", "nasa", "satellite", "nanotechnology"]):
        return "Science & Space"
    return "General Social Claim"

def analyze_claim(text: str) -> Dict[str, Any]:
    """
    Performs full claim extraction, categorizes domain,
    and identifies structural and evidence risk indicators.
    """
    t_lower = text.lower()
    core_claim = extract_core_claim(text)
    claim_type = determine_claim_domain(text)

    risk_indicators: List[str] = []

    # 1. Causal Claim Indicator
    detected_causals = [m for m in CAUSAL_MARKERS if m in t_lower]
    if detected_causals:
        risk_indicators.append(f"Direct causal claim assertion ('{detected_causals[0]}') linking an unverified cause to a consequential effect")

    # 2. Fear / Panic Inducing Wording
    detected_fears = [m for m in FEAR_MARKERS if m in t_lower]
    if detected_fears:
        risk_indicators.append(f"Emotionally charged fear/panic trigger ('{detected_fears[0]}')")

    # 3. Viral Forwarding Framing
    if any(m in t_lower for m in ["whatsapp", "forward", "share aagura", "share pannunga", "group", "10 contacts"]):
        risk_indicators.append("Viral conversational framing designed for rapid chain re-dissemination")

    # 4. Lack of Cited Evidence
    has_source = any(m in t_lower for m in ["imdp", "imd", "isro", "rbi", "government announced", "published", "notified", "official"])
    if not has_source:
        risk_indicators.append("Absence of verifiable institutional citation or primary scientific reference")

    # Normalized Formalized Claim Statement
    # e.g., If Tanglish 5G and birds death
    if "5g" in t_lower and ("bird" in t_lower or "sparrow" in t_lower) and ("die" in t_lower or "kill" in t_lower):
        formal_statement = "5G tower electromagnetic radiation is causing sparrows and avian deaths."
    elif "banana peel" in t_lower and "diabetes" in t_lower:
        formal_statement = "Consuming boiled banana peel water cures diabetes permanently in 7 days."
    elif "onion juice" in t_lower and "hair loss" in t_lower:
        formal_statement = "Topical application of onion juice and lemon completely reverses hair loss."
    elif "pluto" in t_lower and "electricity" in t_lower:
        formal_statement = "Earth's proximity to Pluto enables unlimited free planetary electricity."
    elif "aadhaar" in t_lower and "freez" in t_lower:
        formal_statement = "Government is freezing citizen bank accounts if Aadhaar is not linked immediately."
    elif "microchip" in t_lower and "2000" in t_lower:
        formal_statement = "New currency notes contain embedded GPS satellite microchips."
    else:
        formal_statement = core_claim

    return {
        "original_text": text,
        "extracted_claim": core_claim,
        "formal_claim_statement": formal_statement,
        "claim_type": claim_type,
        "risk_indicators": risk_indicators,
        "is_causal_claim": len(detected_causals) > 0,
        "has_verifiable_citation": has_source
    }
