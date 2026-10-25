"""
Explainability Engine for Tamil-English (Tanglish) Misinformation Detection.
Extracts interpretable linguistic warning signals, sensationalism, urgency,
and hoax markers, explicitly distinguishing model embeddings from rule-based evidence.
"""

import re
from typing import Dict, Any, List

# 1. Sensational Wording
SENSATIONAL_MARKERS = [
    "breaking news", "breaking", "shocking", "must see", "viral tip", "viral video",
    "danger", "disaster", "mind blowing", "unbelievable", "secret revealed",
    "omg", "avlo thaan", "bayangaram", "athiradi", "paraparapu", "kalavaram",
    "hidden truth", "open secret"
]

# 2. Urgency & Fear-Based Language
URGENCY_MARKERS = [
    "immediately", "urgent", "immediate ah", "urgent alert", "hurry", "last chance",
    "before midnight", "tonight 12 pm", "warning alert", "threat", "risk",
    "seekiram", "ippove", "thideer", "bayam", "danger", "deadly", "fatal",
    "mandatory alert", "emergency", "avasiyam", "dont ignore"
]

# 3. Unverified Health / Miracle Claims
HEALTH_HOAX_MARKERS = [
    "cure cancer", "cancer cells", "cure diabetes", "permanent cure", "overnight cure",
    "in 7 days", "in 2 days", "without insulin", "no need for hospital", "doctor secret",
    "heart attack prevent", "kidney damage", "boiled banana peel", "onion juice",
    "garlic with honey", "turmeric and lemon", "baking soda cure", "neem leaf juice",
    "kashayam kudicha", "multi variant viruses", "10 seconds la death", "corona cure",
    "dengue cure"
]

# 4. Financial & Phishing Scam Claims
FINANCIAL_SCAM_MARKERS = [
    "free recharge", "credit aagum", "bank account la", "free rs", "daily rs",
    "lottery win", "cashback grant", "pm modi birthday offer", "free laptop",
    "digital youth scheme", "freeze all bank accounts", "aadhaar link within tonight",
    "unauthorized portal", "claim reward", "earn money daily", "guaranteed income"
]

# 5. Phishing Links & Download Triggers
PHISHING_MARKERS = [
    "click this link", "link below", "download apk", "click here", "fill google form",
    "register immediately", "tap the link", "share link", "open this url",
    "http://", "https://", "bit.ly", "t.co", "download panna"
]

# 6. Viral Forwarding & Social Chain Patterns
VIRAL_FORWARD_MARKERS = [
    "whatsapp la share aagura", "share pannunga", "forward to all", "forward message",
    "share max", "10 contacts ku send", "ellarkum share pannunga", "status la podunga",
    "viral message", "forward panranga", "idha share pannunga", "group la share"
]

# 7. Conspiracy Theories & Tech Rumors
CONSPIRACY_MARKERS = [
    "5g tower radiation", "5g tower rays", "sparrows and birds ah kill", "birds die aagudhu",
    "microchips in 2000 rupee", "satellite tracking", "black money tracker",
    "total darkness across earth", "solar storm total darkness", "pluto planet earth",
    "free electricity pluto", "plastic rice", "artificial egg", "sell panranga supermarkets",
    "internet shutdown 2 hours", "trai daily shutdown", "ban all old 4g smartphones"
]

# 8. Authority Impersonation
AUTHORITY_IMPERSONATION = [
    "unesco declared", "unesco selected", "nasa confirms", "govt secretly",
    "trai new rule", "rbi freezing", "supreme court order leaked", "who confirmed"
]

# 9. Unsupported Numerical / Absolute Claims
NUMERICAL_ABSOLUTES = [
    "100% guaranteed", "100%", "in 10 seconds", "in 2 days", "7 days la",
    "in 24 hours", "permanent ah", "forever", "completely eliminate", "zero side effects"
]

# 10. Official Institution Trust Anchors
OFFICIAL_ANCHORS = [
    "tn government", "tamil nadu government", "isro", "rbi", "reserve bank of india",
    "chennai metro", "high court", "madras high court", "iit madras", "tangedco",
    "imd", "chennai corporation", "southern railway", "anna university"
]

def analyze_explainability(text: str, muril_conf: float = 0.0, indic_conf: float = 0.0, best_label: str = "Fake") -> Dict[str, Any]:
    """
    Examines text for rule-based suspicious linguistic evidence,
    and returns a structured explainability profile.
    """
    text_lower = text.lower()
    signals: List[Dict[str, Any]] = []

    # 1. Sensational Wording
    found_sens = [m for m in SENSATIONAL_MARKERS if m in text_lower]
    if found_sens:
        signals.append({
            "category": "Sensationalism",
            "name": "Sensationalist & Clickbait Language",
            "severity": "HIGH" if len(found_sens) > 1 else "MEDIUM",
            "evidence": found_sens,
            "explanation": "Uses dramatic framing to trigger emotional reaction rather than factual reporting."
        })

    # 2. Urgency & Fear
    found_urg = [m for m in URGENCY_MARKERS if m in text_lower]
    if found_urg:
        signals.append({
            "category": "Urgency & Fear",
            "name": "Artificial Urgency / Panic Induction",
            "severity": "HIGH",
            "evidence": found_urg,
            "explanation": "Demands immediate action or instills fear to discourage critical reflection."
        })

    # 3. Health Hoax
    found_hlth = [m for m in HEALTH_HOAX_MARKERS if m in text_lower]
    if found_hlth:
        signals.append({
            "category": "Health Misinformation",
            "name": "Unverified Medical Remedy or Instant Cure",
            "severity": "CRITICAL",
            "evidence": found_hlth,
            "explanation": "Makes miraculous health recovery claims without clinical peer review or medical credentials."
        })

    # 4. Financial Scam
    found_fin = [m for m in FINANCIAL_SCAM_MARKERS if m in text_lower]
    if found_fin:
        signals.append({
            "category": "Financial / Scam Risk",
            "name": "Unrealistic Financial Incentive or Coercion",
            "severity": "HIGH",
            "evidence": found_fin,
            "explanation": "Promises free money/rewards or threatens financial loss (e.g. bank account freeze)."
        })

    # 5. Phishing Links
    found_phish = [m for m in PHISHING_MARKERS if m in text_lower]
    if found_phish:
        signals.append({
            "category": "Phishing & Malware",
            "name": "Call-to-Action Link or APK Download",
            "severity": "CRITICAL",
            "evidence": found_phish,
            "explanation": "Directs users to click unverified hyperlinks or download third-party applications."
        })

    # 6. Viral Forward Chains
    found_viral = [m for m in VIRAL_FORWARD_MARKERS if m in text_lower]
    if found_viral:
        signals.append({
            "category": "Viral Amplification",
            "name": "Social Media Chain Forwarding Syntax",
            "severity": "MEDIUM",
            "evidence": found_viral,
            "explanation": "Contains explicit instructions to re-share across groups ('forward to all', 'share max')."
        })

    # 7. Conspiracy & Tech Hoaxes
    found_consp = [m for m in CONSPIRACY_MARKERS if m in text_lower]
    if found_consp:
        signals.append({
            "category": "Conspiracy / Tech Hoax",
            "name": "Technological or Scientific Pseudofact",
            "severity": "HIGH",
            "evidence": found_consp,
            "explanation": "Alleges hidden technological dangers (5G radiation, microchips in currency) lacking scientific consensus."
        })

    # 8. Authority Impersonation
    found_auth = [m for m in AUTHORITY_IMPERSONATION if m in text_lower]
    if found_auth:
        signals.append({
            "category": "Authority Impersonation",
            "name": "False Credentialing / Unverified Official Citation",
            "severity": "HIGH",
            "evidence": found_auth,
            "explanation": "Invokes prominent organizations (NASA, UNESCO, Govt) falsely to manufacture credibility."
        })

    # 9. Unsupported Numerical Absolutes
    found_nums = [m for m in NUMERICAL_ABSOLUTES if m in text_lower]
    if found_nums:
        signals.append({
            "category": "Unsupported Absolutes",
            "name": "Uncalibrated Absolute Figures",
            "severity": "MEDIUM",
            "evidence": found_nums,
            "explanation": "Quotes 100% guarantees or unrealistic timelines without empirical backing."
        })

    # 10. Excessive Punctuation
    punct_matches = re.findall(r"[!?]{2,}", text)
    if punct_matches:
        signals.append({
            "category": "Stylometry",
            "name": "Excessive Emphatic Punctuation",
            "severity": "LOW",
            "evidence": list(set(punct_matches)),
            "explanation": "Repeated exclamation or question marks are characteristic of deceptive emotional appeals."
        })

    # 11. Excessive Capitalization
    words = text.split()
    caps_words = [w for w in words if len(w) >= 3 and w.isupper() and w.isalpha()]
    if len(caps_words) >= 2:
        signals.append({
            "category": "Stylometry",
            "name": "Excessive Capitalization (Shouting)",
            "severity": "LOW",
            "evidence": caps_words[:5],
            "explanation": "Capitalized words indicate sensationalist shouting, common in deceptive viral broadcasts."
        })

    # 12. Institutional Anchors (Credibility Dampener)
    found_official = [m for m in OFFICIAL_ANCHORS if m in text_lower]
    has_official_anchor = len(found_official) > 0

    # Calculate Linguistic Risk Signal Score (0 to 100)
    severity_weights = {"CRITICAL": 35, "HIGH": 25, "MEDIUM": 15, "LOW": 8}
    raw_signal_score = sum(severity_weights.get(s["severity"], 10) for s in signals)
    
    if has_official_anchor and best_label == "Real":
        # Official patterns dampen suspicion
        raw_signal_score = max(0, raw_signal_score - 30)

    signal_score = min(100, raw_signal_score)

    # Narrative Summary
    if signals:
        top_cats = ", ".join(list(dict.fromkeys([s["category"] for s in signals]))[:3])
        summary_text = (
            f"Detected {len(signals)} interpretable linguistic warning indicator(s) spanning {top_cats}. "
            f"Syntactic patterns align with known deceptive social media dissemination strategies."
        )
    else:
        summary_text = (
            "No high-risk sensationalist, urgency, or pseudo-scientific markers detected. "
            "Text exhibits neutral linguistic syntax."
        )

    return {
        "signals_count": len(signals),
        "signals": signals,
        "signal_score": signal_score,
        "summary": summary_text,
        "has_official_anchor": has_official_anchor,
        "official_anchors_detected": found_official,
        "distinction_note": (
            "Model prediction is computed independently by transformer sentence embeddings (MuRIL & IndicBERT). "
            "Linguistic warning signals represent transparent, rule-based evidence extracted for explainability."
        )
    }
