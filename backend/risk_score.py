"""
Transparent Misinformation Risk Scoring Engine.
Computes a mathematically interpretable composite risk score (0-100) based on
Model Evidence, Inter-Model Agreement, Linguistic Signals, and Tanglish Robustness.
"""

from typing import Dict, Any

# Transparent Linear Combination Weights (Sum = 1.0)
WEIGHT_MODEL_EVIDENCE = 0.40
WEIGHT_MODEL_AGREEMENT = 0.25
WEIGHT_RISK_SIGNALS = 0.20
WEIGHT_ROBUSTNESS = 0.15

def calculate_misinformation_risk_score(
    muril_label: str,
    muril_prob_fake: float,
    indic_label: str,
    indic_prob_fake: float,
    signal_score: float,
    robustness_score: float
) -> Dict[str, Any]:
    """
    Computes transparent misinformation risk score with complete component breakdown.
    All components normalized to [0, 100].
    """
    # 1. Model Evidence (0-100)
    # Ensemble probability that content is Fake
    avg_fake_prob = (muril_prob_fake + indic_prob_fake) / 2.0
    model_evidence = round(avg_fake_prob * 100.0, 1)

    # 2. Model Agreement (0-100)
    is_m_fake = (muril_label.strip().lower() == "fake")
    is_i_fake = (indic_label.strip().lower() == "fake")

    if is_m_fake and is_i_fake:
        agreement_evidence = 100.0  # Consensus Fake
    elif is_m_fake or is_i_fake:
        agreement_evidence = 50.0   # Split verdict / Disagreement
    else:
        agreement_evidence = 0.0    # Consensus Real

    # 3. Linguistic Risk Signals (0-100)
    risk_signals_evidence = round(max(0.0, min(100.0, signal_score)), 1)

    # 4. Robustness Factor (0-100)
    # If content leans fake, high robustness means the misinformation is persistent under perturbation.
    # If content leans real, high robustness means the legitimacy is persistent, so risk is minimal.
    if avg_fake_prob >= 0.5:
        robustness_evidence = round(robustness_score, 1)
    else:
        robustness_evidence = round(max(0.0, 100.0 - robustness_score), 1)

    # Composite Weighted Sum
    composite_score = (
        (WEIGHT_MODEL_EVIDENCE * model_evidence) +
        (WEIGHT_MODEL_AGREEMENT * agreement_evidence) +
        (WEIGHT_RISK_SIGNALS * risk_signals_evidence) +
        (WEIGHT_ROBUSTNESS * robustness_evidence)
    )
    final_score = int(round(max(0.0, min(100.0, composite_score))))

    # Risk Level Categorization
    if final_score >= 80:
        risk_level = "CRITICAL"
        risk_color = "rose"
        risk_label = "CRITICAL MISINFORMATION RISK"
        risk_summary = "High cross-model fake consensus corroborated by dense sensational/hoax linguistic markers."
    elif final_score >= 60:
        risk_level = "HIGH"
        risk_color = "orange"
        risk_label = "HIGH MISINFORMATION RISK"
        risk_summary = "Substantial model evidence and suspicious linguistic signals detected."
    elif final_score >= 35:
        risk_level = "MODERATE"
        risk_color = "amber"
        risk_label = "MODERATE MISINFORMATION RISK"
        risk_summary = "Elevated ambiguity due to partial model agreement or borderline indicators."
    else:
        risk_level = "LOW"
        risk_color = "emerald"
        risk_label = "LOW RISK / VERIFIED CREDIBLE"
        risk_summary = "Content exhibits standard journalistic syntax with consensus credible model classification."

    return {
        "final_risk_score": final_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_label": risk_label,
        "risk_summary": risk_summary,
        "weights": {
            "model_evidence_weight": WEIGHT_MODEL_EVIDENCE,
            "model_agreement_weight": WEIGHT_MODEL_AGREEMENT,
            "risk_signals_weight": WEIGHT_RISK_SIGNALS,
            "robustness_weight": WEIGHT_ROBUSTNESS
        },
        "breakdown": {
            "model_evidence": model_evidence,
            "model_agreement": agreement_evidence,
            "risk_signals": risk_signals_evidence,
            "robustness": robustness_evidence
        },
        "disclaimer": (
            "The Misinformation Risk Score is a multi-criteria decision metric combining transformer probabilities, "
            "inter-model agreement, linguistic heuristics, and perturbation stability. It is not an assertion of absolute objective truth."
        )
    }
