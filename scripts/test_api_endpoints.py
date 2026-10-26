import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8")
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

print("1. Testing GET /api/stats ...")
r = client.get("/api/stats")
assert r.status_code == 200, f"Stats failed: {r.status_code}"
stats = r.json()
print("   Total samples:", stats.get("total_samples"), "Base corpus:", stats.get("base_corpus_count"), "Live count:", stats.get("realtime_live_count"))

print("2. Testing GET /api/robustness-benchmark ...")
r = client.get("/api/robustness-benchmark")
assert r.status_code == 200, f"Robustness failed: {r.status_code}"
metrics = r.json().get("standard_vs_robustness", {}).get("metrics", [])
print(f"   Benchmark metrics loaded: {len(metrics)} rows")

print("3. Testing GET /api/realtime-dataset ...")
r = client.get("/api/realtime-dataset")
assert r.status_code == 200, f"Realtime dataset failed: {r.status_code}"
print("   Realtime dataset total:", r.json().get("total_realtime_items"))

print("4. Testing GET & POST /api/config/api-key ...")
r = client.get("/api/config/api-key")
assert r.status_code == 200
r_post = client.post("/api/config/api-key", json={"api_key": ""})
assert r_post.status_code == 200
print("   API config endpoint functional: has_key =", r_post.json().get("has_key"))

print("5. Testing file downloads ...")
for fname in ["realtime_live_dataset.json", "Tamil_English_Fake_Real_Dataset_Full.csv", "fake_news_model.zip"]:
    r = client.get(f"/api/download/{fname}")
    assert r.status_code == 200, f"Download {fname} failed: {r.status_code}"
    print(f"   Download {fname}: HTTP {r.status_code}, {len(r.content)} bytes")

print("\nALL FASTAPI ENDPOINTS VERIFIED SUCCESSFULLY!")
