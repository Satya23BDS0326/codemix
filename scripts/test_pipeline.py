import sys, os, json
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8")
from backend.dual_model_classifier import init_models, predict_dual_models
from backend.realtime_verifier import get_realtime_dataset_stats

print("Initializing / prewarming models...")
init_models()

print("\n--- TEST 1: Tanglish Hoax (Midnight cosmic ray warning) ---")
res1 = predict_dual_models("NASA warning sonnanga midnight phone use panna koodadhu cosmic rays attack varum")
print("MuRIL:", res1["muril_results"]["label_name"], f"{res1['muril_results']['confidence']}%")
print("IndicBERT:", res1["indicbert_results"]["label_name"], f"{res1['indicbert_results']['confidence']}%")
print("Base Model:", res1["base_model_results"]["predicted_label"], f"{res1['base_model_results']['confidence']}%")
print("Selected Model:", res1["model_selection_decision"]["selected_model"])
print("Selection Summary:", res1["model_selection_decision"]["decision_summary"])
print("Real-Time Fact Check:", res1["realtime_verification"]["verdict"])
print("Fact Checker:", res1["realtime_verification"]["fact_checker"])
print("Latency:", f"{res1['realtime_verification']['latency_ms']} ms")

print("\n--- TEST 2: Novel query to test dynamic auto-ingestion ---")
res2 = predict_dual_models("Breaking news: Anna University launches novel AI robotics workshop tomorrow morning")
print("Real-Time Verdict:", res2["realtime_verification"]["verdict"])
print("Auto Ingested to Dataset:", res2["realtime_dataset_ingested"])

stats = get_realtime_dataset_stats()
print("\nLive Dynamic Dataset Stats:", stats)
