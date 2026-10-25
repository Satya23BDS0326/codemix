"""
Model Agreement and Decision Reliability Engine.
Evaluates consensus and divergence between Google MuRIL and IndicBERT encoders,
computing a calibrated Decision Reliability metric (HIGH, MEDIUM, LOW).
"""

from typing import Dict, Any

def evaluate_model_agreement(
    muril_label: str,
    muril_conf: float,
    indic_label: str,
    indic_conf: float
) -> Dict[str, Any]:
    """
    Computes inter-model agreement, disagreement diagnosis, and decision reliability.
    """
    labels_agree = (muril_label.strip().lower() == indic_label.strip().lower())
    avg_conf = (muril_conf + indic_conf) / 2.0
    min_conf = min(muril_conf, indic_conf)
    max_conf = max(muril_conf, indic_conf)
    conf_spread = abs(muril_conf - indic_conf)

    # State Diagnosis
    if not labels_agree:
        agreement_state = "DISAGREEMENT"
        decision_reliability = "LOW"
        reliability_color = "rose"
        reliability_score = 35.0
        headline = "Model Disagreement Detected"
        diagnosis = (
            f"Google MuRIL predicted '{muril_label}' ({muril_conf}%) while IndicBERT predicted "
            f"'{indic_label}' ({indic_conf}%). The transformer representations diverged on "
            f"token semantics, indicating high borderline ambiguity."
        )
    elif min_conf < 60.0:
        agreement_state = "LOW_CONFIDENCE"
        decision_reliability = "LOW"
        reliability_color = "amber"
        reliability_score = round(min_conf * 0.7, 1)
        headline = "Prediction Uncertain (Near Decision Boundary)"
        diagnosis = (
            f"Both models agreed on '{muril_label}', but confidence levels hover near the "
            f"50% decision boundary (MuRIL: {muril_conf}%, IndicBERT: {indic_conf}%). "
            f"Classification has low margin of safety."
        )
    elif avg_conf >= 75.0 and labels_agree:
        agreement_state = "HIGH_AGREEMENT"
        decision_reliability = "HIGH"
        reliability_color = "emerald"
        reliability_score = round(min(100.0, avg_conf + (5.0 if conf_spread < 10 else 0.0)), 1)
        headline = "High Inter-Model Consensus"
        diagnosis = (
            f"Both Google MuRIL ({muril_conf}%) and IndicBERT ({indic_conf}%) independently "
            f"converged on '{muril_label}' with strong confidence (spread: {conf_spread:.1f}%)."
        )
    else:
        agreement_state = "MODERATE_AGREEMENT"
        decision_reliability = "MEDIUM"
        reliability_color = "indigo"
        reliability_score = round(avg_conf, 1)
        headline = "Moderate Consensus"
        diagnosis = (
            f"Both models agreed on '{muril_label}', but one model exhibits moderate confidence "
            f"(MuRIL: {muril_conf}%, IndicBERT: {indic_conf}%)."
        )

    return {
        "labels_agree": labels_agree,
        "agreement_state": agreement_state,
        "decision_reliability": decision_reliability,
        "reliability_color": reliability_color,
        "reliability_score": reliability_score,
        "confidence_spread": round(conf_spread, 1),
        "headline": headline,
        "diagnosis": diagnosis,
        "calibration_disclaimer": (
            "Decision Reliability reflects model consensus and distance from decision boundary; "
            "it is not guaranteed factual truth."
        )
    }
