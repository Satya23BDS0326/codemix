"""
Test all FastAPI endpoints using TestClient.
"""

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_endpoints():
    print("Testing /api/health...")
    r = client.get("/api/health")
    assert r.status_code == 200, r.text
    print("Health:", r.json()["status"])

    sample_text = "5G tower radiation nala birds die aagudhu"

    print("\nTesting POST /api/predict...")
    r = client.post("/api/predict", json={"text": sample_text})
    assert r.status_code == 200, r.text
    pred_data = r.json()
    print("Prediction:", pred_data["best_model_recommendation"]["predicted_label"])
    print("Decision Reliability:", pred_data["decision_reliability"])
    print("Risk Score:", pred_data["risk_score_analysis"]["final_risk_score"])
    print("Claim:", pred_data["claim_analysis"]["formal_claim_statement"])
    assert "explainability" in pred_data
    assert "claim_analysis" in pred_data
    assert "agreement_analysis" in pred_data

    print("\nTesting POST /api/robustness...")
    r = client.post("/api/robustness", json={"text": sample_text})
    assert r.status_code == 200, r.text
    rob_data = r.json()
    print("Robustness Score:", rob_data["robustness_score"], "%")
    print("Variants Tested:", rob_data["total_variants_tested"])
    assert "variants_table" in rob_data

    print("\nTesting POST /api/explain...")
    r = client.post("/api/explain", json={"text": sample_text})
    assert r.status_code == 200, r.text
    exp_data = r.json()
    print("Signals Count:", exp_data["signals_count"])

    print("\nTesting POST /api/claim-analysis...")
    r = client.post("/api/claim-analysis", json={"text": sample_text})
    assert r.status_code == 200, r.text
    claim_data = r.json()
    print("Extracted Claim:", claim_data["extracted_claim"])

    print("\nTesting GET /api/robustness-benchmark...")
    r = client.get("/api/robustness-benchmark")
    assert r.status_code == 200, r.text
    bm_data = r.json()
    print("Standard vs Robustness Metrics:", len(bm_data["standard_vs_robustness"]["metrics"]))

    print("\nTesting Empty Query Error Handling...")
    r = client.post("/api/predict", json={"text": ""})
    assert r.status_code == 400
    print("Empty text properly returned 400 Bad Request.")

    print("\n[SUCCESS] ALL API ENDPOINTS VERIFIED!")

if __name__ == "__main__":
    test_endpoints()
