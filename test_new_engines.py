"""
Unit test script for Explainable and Robustness-Aware Misinformation Intelligence System.
Tests:
1. Explainability Engine (13+ signals)
2. Claim Extraction Engine
3. Model Agreement Engine
4. Robustness Analyzer & Perturbation Generator
5. Misinformation Risk Scoring
6. Benchmark Results Generator
"""

import sys

def test_all():
    print("=== 1. Testing Explainability Engine ===")
    from backend.explainability_engine import analyze_explainability
    text1 = "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu, immediate ah stop panna solranga!!!"
    res1 = analyze_explainability(text1, muril_conf=98.4, indic_conf=91.2, best_label="Fake")
    print(f"Signals Count: {res1['signals_count']}, Score: {res1['signal_score']}")
    for s in res1['signals']:
        print(f"  - [{s['severity']}] {s['category']}: {s['name']} (evidence: {s['evidence']})")
    assert res1['signals_count'] >= 3, "Expected at least 3 suspicious signals"

    print("\n=== 2. Testing Claim Extraction Engine ===")
    from backend.claim_extractor import analyze_claim
    claim_res = analyze_claim(text1)
    print(f"Original: {claim_res['original_text']}")
    print(f"Extracted Claim: {claim_res['extracted_claim']}")
    print(f"Formal Statement: {claim_res['formal_claim_statement']}")
    print(f"Domain: {claim_res['claim_type']}")
    print(f"Risk Indicators: {claim_res['risk_indicators']}")
    assert "5G" in claim_res['extracted_claim']
    assert len(claim_res['risk_indicators']) >= 2

    print("\n=== 3. Testing Model Agreement Engine ===")
    from backend.agreement_engine import evaluate_model_agreement
    # Case A: High Agreement
    agr_a = evaluate_model_agreement("Fake", 94.0, "Fake", 91.0)
    print(f"Consensus Case: State={agr_a['agreement_state']}, Reliability={agr_a['decision_reliability']}")
    assert agr_a['decision_reliability'] == "HIGH"
    
    # Case B: Disagreement
    agr_b = evaluate_model_agreement("Fake", 72.0, "Real", 68.0)
    print(f"Disagreement Case: State={agr_b['agreement_state']}, Reliability={agr_b['decision_reliability']}")
    assert agr_b['decision_reliability'] == "LOW"

    # Case C: Low Confidence Boundary
    agr_c = evaluate_model_agreement("Fake", 53.0, "Fake", 52.0)
    print(f"Low Confidence Case: State={agr_c['agreement_state']}, Reliability={agr_c['decision_reliability']}")
    assert agr_c['decision_reliability'] == "LOW"

    print("\n=== 4. Testing Misinformation Risk Score ===")
    from backend.risk_score import calculate_misinformation_risk_score
    risk_res = calculate_misinformation_risk_score(
        muril_label="Fake",
        muril_prob_fake=0.95,
        indic_label="Fake",
        indic_prob_fake=0.88,
        signal_score=res1['signal_score'],
        robustness_score=87.5
    )
    print(f"Risk Score: {risk_res['final_risk_score']}/100 - {risk_res['risk_level']}")
    print(f"Breakdown: {risk_res['breakdown']}")
    assert 70 <= risk_res['final_risk_score'] <= 100

    print("\n=== 5. Testing Tanglish Perturbation Generator ===")
    from backend.robustness_analyzer import generate_tanglish_variants
    variants = generate_tanglish_variants(text1)
    print(f"Generated {len(variants)} Tanglish Variants:")
    for v in variants:
        print(f"  [{v['type']}] {v['text']}")
    assert len(variants) >= 5

    print("\n=== 6. Testing Benchmark Results Generator ===")
    from backend.benchmark_eval import get_or_create_benchmark_results
    bm = get_or_create_benchmark_results()
    print(f"Dataset Name: {bm['dataset_name']}")
    print(f"Standard vs Robustness Metrics count: {len(bm['standard_vs_robustness']['metrics'])}")
    print(f"3-Way Experiment Groups: {len(bm['three_way_linguistic_experiment']['groups'])}")
    assert len(bm['standard_vs_robustness']['metrics']) >= 6

    print("\n[SUCCESS] ALL MODULAR ENGINES PASSED UNIT TESTS!")

if __name__ == "__main__":
    test_all()
