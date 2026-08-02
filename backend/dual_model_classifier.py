import os
import pickle
import torch
import numpy as np
from typing import Dict, Any, List
from transformers import AutoTokenizer, AutoModel

BACKEND_DATA = r"C:\Users\balla\OneDrive\Desktop\CodeMix\backend\data"

MURIL_NAME = "google/muril-base-cased"
INDIC_NAME = "bert-base-multilingual-cased"

muril_tok = None
muril_mod = None
indic_tok = None
indic_mod = None
clf_muril = None
clf_indic = None

def init_models():
    global muril_tok, muril_mod, indic_tok, indic_mod, clf_muril, clf_indic
    if muril_tok is None:
        print("Loading MuRIL Encoder...", flush=True)
        muril_tok = AutoTokenizer.from_pretrained(MURIL_NAME)
        muril_mod = AutoModel.from_pretrained(MURIL_NAME)
        muril_mod.eval()

    if indic_tok is None:
        print("Loading IndicBERT Encoder...", flush=True)
        indic_tok = AutoTokenizer.from_pretrained(INDIC_NAME)
        indic_mod = AutoModel.from_pretrained(INDIC_NAME)
        indic_mod.eval()

    muril_clf_path = os.path.join(BACKEND_DATA, "muril_classifier.pkl")
    indic_clf_path = os.path.join(BACKEND_DATA, "indicbert_classifier.pkl")

    if clf_muril is None and os.path.exists(muril_clf_path):
        with open(muril_clf_path, "rb") as f:
            clf_muril = pickle.load(f)

    if clf_indic is None and os.path.exists(indic_clf_path):
        with open(indic_clf_path, "rb") as f:
            clf_indic = pickle.load(f)

TANGLISH_MARKERS = {
    "aagum", "pannuthu", "kudicha", "varudho", "ungalu", "ungaluku", "panranga",
    "bro", "la", "ku", "ah", "panna", "maarum", "irundha", "kitta", "parthu",
    "vanggunga", "potu", "intha", "inga", "unga", "solranga", "vandhu", "namma",
    "pannalam", "podu", "podum", "maari", "thoonguna", "milikkum", "pannuvanga"
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

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts

def get_muril_emb(text: str) -> np.ndarray:
    init_models()
    inputs = muril_tok(text, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        output = muril_mod(**inputs)
    emb = mean_pooling(output, inputs["attention_mask"])
    return emb[0].cpu().numpy()

def get_indic_emb(text: str) -> np.ndarray:
    init_models()
    inputs = indic_tok(text, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        output = indic_mod(**inputs)
    emb = mean_pooling(output, inputs["attention_mask"])
    return emb[0].cpu().numpy()

def analyze_tanglish(text: str) -> Dict[str, Any]:
    words = [w.strip(".,!?\"'()[]{}").lower() for w in text.split() if w.strip()]
    if not words:
        return {"code_mix_type": "English", "cmi": 0.0, "tanglish_pct": 0.0, "english_pct": 100.0}

    tanglish_count = sum(1 for w in words if w in TANGLISH_MARKERS)
    total = len(words)

    if tanglish_count > 0:
        t_pct = round((tanglish_count / total) * 100, 1)
        e_pct = round(100.0 - t_pct, 1)
        cmi = round(min(t_pct, e_pct), 1)
        return {
            "code_mix_type": "Tanglish (Tamil-English)",
            "cmi": cmi,
            "tanglish_pct": t_pct,
            "english_pct": e_pct
        }
    else:
        return {
            "code_mix_type": "English-Mixed",
            "cmi": 0.0,
            "tanglish_pct": 0.0,
            "english_pct": 100.0
        }

def get_risk_factors(text: str, is_fake: bool) -> tuple[List[str], str]:
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

    if not is_fake:
        if any(term in text_lower for term in ["tn government", "isro", "rbi", "chennai metro", "high court", "iit madras", "tangedco"]):
            risks.append("Official institution announcement pattern")
            if "rain" in text_lower or "weather" in text_lower:
                category = "Weather News"
            elif "transport" in text_lower or "metro" in text_lower or "bus" in text_lower:
                category = "Transport"
            elif "court" in text_lower:
                category = "Judiciary"
            elif "isro" in text_lower:
                category = "Science"
            else:
                category = "Public Governance"

    return risks, category

def predict_dual_models(text: str) -> Dict[str, Any]:
    init_models()

    emb_muril = get_muril_emb(text)
    emb_indic = get_indic_emb(text)

    # 1. MuRIL Prediction
    if clf_muril is not None:
        probs_m = clf_muril.predict_proba([emb_muril])[0]
        fake_p_m, real_p_m = float(probs_m[1]), float(probs_m[0])
        label_id_m = 1 if fake_p_m >= 0.5 else 0
    else:
        fake_p_m, real_p_m, label_id_m = 0.5, 0.5, 0

    conf_m = round((fake_p_m if label_id_m == 1 else real_p_m) * 100, 1)

    # 2. IndicBERT Prediction
    if clf_indic is not None:
        probs_i = clf_indic.predict_proba([emb_indic])[0]
        fake_p_i, real_p_i = float(probs_i[1]), float(probs_i[0])
        label_id_i = 1 if fake_p_i >= 0.5 else 0
    else:
        fake_p_i, real_p_i, label_id_i = 0.5, 0.5, 0

    conf_i = round((fake_p_i if label_id_i == 1 else real_p_i) * 100, 1)

    # Select Best Model
    if conf_m >= conf_i:
        best_model = "Google MuRIL"
        best_label = "Fake" if label_id_m == 1 else "Real"
        best_conf = conf_m
        best_reason = "Google MuRIL achieved higher confidence due to its specialized transliterated & romanized Indic pre-training."
    else:
        best_model = "IndicBERT"
        best_label = "Fake" if label_id_i == 1 else "Real"
        best_conf = conf_i
        best_reason = "IndicBERT achieved higher confidence score on this query structure."

    cm_analysis = analyze_tanglish(text)
    risks, category = get_risk_factors(text, is_fake=(label_id_m == 1 or label_id_i == 1))

    return {
        "text": text,
        "category": category,
        "code_mix_type": cm_analysis["code_mix_type"],
        "cmi": cm_analysis["cmi"],
        "tanglish_pct": cm_analysis["tanglish_pct"],
        "english_pct": cm_analysis["english_pct"],
        "best_model_recommendation": {
            "model_name": best_model,
            "predicted_label": best_label,
            "confidence": best_conf,
            "reason": best_reason
        },
        "muril_results": {
            "model_name": "Google MuRIL (google/muril-base-cased)",
            "label": label_id_m,
            "label_name": "Fake" if label_id_m == 1 else "Real",
            "confidence": conf_m,
            "probabilities": {"Real": round(real_p_m, 4), "Fake": round(fake_p_m, 4)}
        },
        "indicbert_results": {
            "model_name": "IndicBERT (bert-base-multilingual-cased)",
            "label": label_id_i,
            "label_name": "Fake" if label_id_i == 1 else "Real",
            "confidence": conf_i,
            "probabilities": {"Real": round(real_p_i, 4), "Fake": round(fake_p_i, 4)}
        },
        "risk_factors": risks
    }
