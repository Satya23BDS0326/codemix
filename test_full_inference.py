"""
Test full inference and robustness experiment across MuRIL and IndicBERT.
"""

from backend.dual_model_classifier import predict_dual_models, predict_dual_raw
from backend.robustness_analyzer import run_robustness_experiment

text = "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu, immediate ah stop panna solranga."

print("Running predict_dual_models...")
res = predict_dual_models(text)
print(f"Prediction: {res['best_model_recommendation']['predicted_label']} by {res['best_model_recommendation']['model_name']} ({res['best_model_recommendation']['confidence']}%)")
print(f"Decision Reliability: {res['decision_reliability']} ({res['agreement_analysis']['headline']})")
print(f"Risk Score: {res['risk_score_analysis']['final_risk_score']}/100 ({res['risk_score_analysis']['risk_level']})")
print(f"Extracted Claim: {res['claim_analysis']['formal_claim_statement']}")
print(f"Domain: {res['claim_analysis']['claim_type']}")
print(f"Signals Count: {res['explainability']['signals_count']}")

print("\nRunning Robustness Perturbation Experiment...")
exp = run_robustness_experiment(
    original_text=text,
    original_muril_res=res["muril_results"],
    original_indic_res=res["indicbert_results"],
    predict_fn=predict_dual_raw
)
print(f"Robustness Score: {exp['robustness_score']}%")
print(f"MuRIL Stability: {exp['muril_stability_pct']}% | IndicBERT Stability: {exp['indic_stability_pct']}%")
print(f"More Robust Model: {exp['more_robust_model']}")
print(f"Research Observation: {exp['research_observation']}")
print(f"Variants Table Count: {len(exp['variants_table'])}")
for r in exp['variants_table']:
    print(f"  [{r['variant_id']}] {r['type']}: MuRIL={r['muril_label']}({r['muril_conf']}%), Indic={r['indic_label']}({r['indic_conf']}%), Agr={'✓' if r['agreement'] else '⚠'}, Stable={'✓' if r['overall_stable'] else 'FAIL'}")

print("\n[SUCCESS] Full Inference & Robustness Experiment executed flawlessly!")
