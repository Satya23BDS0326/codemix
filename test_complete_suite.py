"""
Comprehensive Test Suite covering all USER_REQUEST scenarios:
1. Normal Real input
2. Normal Fake input
3. Tanglish input
4. Spelling variation
5. Model disagreement case
6. Empty/invalid input
7. Robustness experiment
"""

from fastapi.testclient import TestClient
from backend.app import app
import json

client = TestClient(app)

def run_tests():
    print("=" * 70)
    print("CODEMIX RESEARCH INTELLIGENCE SYSTEM — COMPREHENSIVE VERIFICATION")
    print("=" * 70)

    # Test 1: Normal Real Input
    print("\n[TEST 1] Normal Real Input:")
    t1 = "TN Government announced tomorrow local holiday for Chennai schools due to heavy rain forecast by IMD."
    r1 = client.post("/api/predict", json={"text": t1}).json()
    print(f"  Input: {t1[:60]}...")
    print(f"  Best Model: {r1['best_model_recommendation']['model_name']} -> {r1['best_model_recommendation']['predicted_label']} ({r1['best_model_recommendation']['confidence']}%)")
    print(f"  Decision Reliability: {r1['decision_reliability']}")
    print(f"  Risk Score: {r1['risk_score_analysis']['final_risk_score']}/100 ({r1['risk_score_analysis']['risk_level']})")
    assert r1['best_model_recommendation']['predicted_label'] == "Real"

    # Test 2: Normal Fake Input
    print("\n[TEST 2] Normal Fake Input:")
    t2 = "Drinking boiled banana peel water every morning will cancel diabetes in just 7 days without insulin."
    r2 = client.post("/api/predict", json={"text": t2}).json()
    print(f"  Input: {t2[:60]}...")
    print(f"  Best Model: {r2['best_model_recommendation']['model_name']} -> {r2['best_model_recommendation']['predicted_label']} ({r2['best_model_recommendation']['confidence']}%)")
    print(f"  Extracted Claim: {r2['claim_analysis']['formal_claim_statement']}")
    print(f"  Risk Score: {r2['risk_score_analysis']['final_risk_score']}/100 ({r2['risk_score_analysis']['risk_level']})")
    assert r2['best_model_recommendation']['predicted_label'] == "Fake"

    # Test 3: Tanglish Input
    print("\n[TEST 3] Tanglish Code-Mixed Input:")
    t3 = "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu, immediate ah stop panna solranga."
    r3 = client.post("/api/predict", json={"text": t3}).json()
    print(f"  Input: {t3}")
    print(f"  CMI: {r3['cmi']}% ({r3['code_mix_type']})")
    print(f"  Extracted Claim: {r3['claim_analysis']['formal_claim_statement']}")
    print(f"  Signals Flagged: {r3['explainability']['signals_count']}")
    for s in r3['explainability']['signals']:
        print(f"    - {s['name']} (severity: {s['severity']})")
    assert r3['cmi'] > 0

    # Test 4: Spelling Variation Input
    print("\n[TEST 4] Colloquial Spelling Variation Input:")
    t4 = "Whatsapp la share aagura message: 5G tower kathir vanthu sparrows ah kill panuthu immediate ah nirutha pana solluranga"
    r4 = client.post("/api/predict", json={"text": t4}).json()
    print(f"  Input: {t4[:60]}...")
    print(f"  MuRIL: {r4['muril_results']['label_name']} ({r4['muril_results']['confidence']}%)")
    print(f"  IndicBERT: {r4['indicbert_results']['label_name']} ({r4['indicbert_results']['confidence']}%)")
    print(f"  Decision Reliability: {r4['decision_reliability']}")
    assert r4['best_model_recommendation']['predicted_label'] == "Fake"

    # Test 5: Model Agreement / Disagreement Case
    print("\n[TEST 5] Model Agreement & Decision Reliability Diagnostic:")
    from backend.agreement_engine import evaluate_model_agreement
    disagreement_case = evaluate_model_agreement("Fake", 78.0, "Real", 65.0)
    print(f"  Disagreement Case Diagnostic: {disagreement_case['headline']}")
    print(f"  Reliability: {disagreement_case['decision_reliability']}")
    print(f"  Diagnosis: {disagreement_case['diagnosis']}")
    assert disagreement_case['decision_reliability'] == "LOW"

    # Test 6: Empty / Invalid Input
    print("\n[TEST 6] Empty/Invalid Input Handling:")
    r6_empty = client.post("/api/predict", json={"text": ""})
    print(f"  Empty text status: {r6_empty.status_code} ({r6_empty.json()['detail']})")
    assert r6_empty.status_code == 400

    r6_spaces = client.post("/api/predict", json={"text": "   "})
    print(f"  Whitespace status: {r6_spaces.status_code} ({r6_spaces.json()['detail']})")
    assert r6_spaces.status_code == 400

    # Test 7: Tanglish Robustness Experiment
    print("\n[TEST 7] Tanglish Robustness Experiment:")
    r7 = client.post("/api/robustness", json={"text": t3}).json()
    print(f"  Robustness Score: {r7['robustness_score']}%")
    print(f"  MuRIL Stability: {r7['muril_stability_pct']}% | IndicBERT Stability: {r7['indic_stability_pct']}%")
    print(f"  More Robust: {r7['more_robust_model']}")
    print(f"  Total Variants Evaluated: {r7['total_variants_tested']}")
    print(f"  Variants Table Sample:")
    for v in r7['variants_table'][:3]:
        print(f"    - [{v['type']}]: MuRIL={v['muril_label']}, Indic={v['indic_label']}, Stable={'✓' if v['overall_stable'] else 'FAIL'}")
    assert r7['total_variants_tested'] >= 5
    assert r7['robustness_score'] > 0

    print("\n" + "=" * 70)
    print("[ALL 7/7 TEST SCENARIOS PASSED WITH COMPLETE VALIDATION!]")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
