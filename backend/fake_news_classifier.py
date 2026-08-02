import os
import re
import pickle
import numpy as np
from typing import Dict, Any, List

TANGLISH_MARKERS = {
    "aagum", "pannuthu", "kudicha", "varudho", "ungalu", "ungaluku", "panranga",
    "bro", "la", "ku", "ah", "panna", "maarum", "irundha", "kitta", "parthu",
    "vanggunga", "potu", "intha", "inga", "unga", "solranga", "vandhu", "namma",
    "pannalam", "podu", "podum", "maari", "thoonguna", "milikkum", "pannuvanga"
}

TELUGU_MARKERS = {
    "unnaya", "unnayi", "undi", "vundi", "ledu", "kavali", "chestunna",
    "chesta", "chey", "cheyali", "enti", "ento", "meeru", "nenu",
    "vaadu", "vaallu", "manam", "naaku", "neeku", "vaariki",
    "lo", "ki", "nunchi", "tho", "ga", "ante", "kosam", "chala", "koncham"
}

PHISHING_MARKERS = [
    "click", "link", "free", "recharge", "claim", "grant", "lakhs", "apk",
    "whatsapp", "forward", "warning", "urgent", "secret", "100%", "guaranteed",
    "cashback", "lottery", "gift", "unauthorized website", "non-govt portal"
]

HEALTH_HOAX_MARKERS = [
    "cure", "cancer", "diabetes", "permanent", "overnight", "hours", "doctor secret",
    "heart attack", "kidney", "fat", "banana peel", "onion juice", "garlic",
    "coconut oil", "turmeric", "baking soda", "neem"
]

TECH_HOAX_MARKERS = [
    "5g tower", "sparrows", "radiation", "microchip", "2000 rupee", "brain damage",
    "earphone", "battery blast", "camera turn on", "location tracker", "listening device"
]

def analyze_code_mixing(text: str) -> Dict[str, Any]:
    words = [w.strip(".,!?\"'()[]{}").lower() for w in text.split() if w.strip()]
    if not words:
        return {"code_mix_type": "English", "cmi": 0.0, "tanglish_pct": 0.0, "english_pct": 100.0}

    tanglish_count = sum(1 for w in words if w in TANGLISH_MARKERS)
    telugu_count = sum(1 for w in words if w in TELUGU_MARKERS)
    total = len(words)

    if tanglish_count > 0:
        t_pct = round((tanglish_count / total) * 100, 1)
        e_pct = round(100.0 - t_pct, 1)
        cmi = round(min(t_pct, e_pct), 1)
        return {
            "code_mix_type": "Tanglish",
            "cmi": cmi,
            "tanglish_pct": t_pct,
            "english_pct": e_pct
        }
    elif telugu_count > 0:
        tel_pct = round((telugu_count / total) * 100, 1)
        e_pct = round(100.0 - tel_pct, 1)
        cmi = round(min(tel_pct, e_pct), 1)
        return {
            "code_mix_type": "Telugu-English",
            "cmi": cmi,
            "tanglish_pct": tel_pct,
            "english_pct": e_pct
        }
    else:
        return {
            "code_mix_type": "English-Mixed",
            "cmi": 0.0,
            "tanglish_pct": 0.0,
            "english_pct": 100.0
        }

def get_risk_factors_and_category(text: str, is_fake: bool) -> tuple[List[str], str]:
    text_lower = text.lower()
    risks = []
    category = "General News"

    if any(m in text_lower for m in HEALTH_HOAX_MARKERS):
        category = "Health Misinformation"
        if is_fake:
            risks.append("Unverified medical claim or instant cure remedy")
    
    if any(m in text_lower for m in PHISHING_MARKERS):
        if category == "General News":
            category = "Phishing Scam"
        risks.append("Contains call-to-action link, APK download, or cash/gift offer")

    if any(m in text_lower for m in TECH_HOAX_MARKERS):
        if category == "General News":
            category = "Tech Rumor"
        risks.append("Unsubstantiated technology / radiation / conspiracy theory")

    if "forward" in text_lower or "share" in text_lower:
        risks.append("Viral forward chain-message style phrasing")

    if any(term in text_lower for term in ["unesco", "declared", "world best"]):
        if category == "General News":
            category = "Social Media Hoax"
        risks.append("Falsely attributed UNESCO or international award claim")

    if not is_fake:
        if any(term in text_lower for term in ["tn government", "isro", "rbi", "chennai metro", "high court", "iit madras", "tangedco", "police"]):
            risks.append("Official institution/authority announcement pattern")
            if "rain" in text_lower or "weather" in text_lower:
                category = "Weather News"
            elif "transport" in text_lower or "metro" in text_lower or "bus" in text_lower or "train" in text_lower:
                category = "Transport"
            elif "court" in text_lower or "judiciary" in text_lower:
                category = "Judiciary"
            elif "isro" in text_lower or "nasa" in text_lower:
                category = "Science"
            elif "rbi" in text_lower or "bank" in text_lower:
                category = "Finance"
            else:
                category = "Public Utility / Governance"

    return risks, category

def classify_text(text: str, model=None, vectorizer=None) -> Dict[str, Any]:
    cm_analysis = analyze_code_mixing(text)
    
    if model is not None and vectorizer is not None:
        X_vec = vectorizer.transform([text.lower()])
        probs = model.predict_proba(X_vec)[0]
        fake_prob = float(probs[1])
        real_prob = float(probs[0])
        label_id = 1 if fake_prob >= 0.5 else 0
    else:
        text_lower = text.lower()
        fake_score = 0
        if any(m in text_lower for m in PHISHING_MARKERS):
            fake_score += 2
        if any(m in text_lower for m in HEALTH_HOAX_MARKERS):
            fake_score += 2
        if any(m in text_lower for m in TECH_HOAX_MARKERS):
            fake_score += 2
        if "forward to" in text_lower or "viral video" in text_lower or "100%" in text_lower or "click link" in text_lower:
            fake_score += 2
        if any(term in text_lower for term in ["announced", "launched", "directed", "issued", "commissioned"]):
            fake_score -= 1.5

        fake_prob = min(0.98, max(0.02, 0.5 + fake_score * 0.15))
        real_prob = 1.0 - fake_prob
        label_id = 1 if fake_prob >= 0.5 else 0

    label_name = "Fake" if label_id == 1 else "Real"
    confidence = round((fake_prob if label_id == 1 else real_prob) * 100, 1)

    risks, category = get_risk_factors_and_category(text, is_fake=(label_id == 1))

    if label_id == 1:
        explanation = f"Classified as FAKE news with {confidence}% confidence. " + \
            (f"Triggered risk indicators: {'; '.join(risks)}." if risks else "Presents linguistic patterns consistent with unverified rumors.")
    else:
        explanation = f"Classified as REAL news with {confidence}% confidence. " + \
            (f"Verified elements: {'; '.join(risks)}." if risks else "Matches authentic news report structure.")

    return {
        "text": text,
        "label": label_id,
        "label_name": label_name,
        "confidence": confidence,
        "probabilities": {
            "Real": round(real_prob, 4),
            "Fake": round(fake_prob, 4)
        },
        "code_mix_type": cm_analysis["code_mix_type"],
        "cmi": cm_analysis["cmi"],
        "tanglish_pct": cm_analysis["tanglish_pct"],
        "english_pct": cm_analysis["english_pct"],
        "category": category,
        "risk_factors": risks,
        "explanation": explanation
    }
