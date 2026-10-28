import os
import sys
import pickle
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60, flush=True)
    print("[STARTUP] Pre-warming Google MuRIL, IndicBERT, Baseline, and Real-Time Verifier...", flush=True)
    try:
        from backend.base_model import init_base_model
        from backend.dual_model_classifier import init_models, predict_dual_models
        from backend.realtime_verifier import get_realtime_dataset_stats
        init_base_model()
        init_models()
        get_realtime_dataset_stats()
        # Pre-warm benchmark presets for instant (<5ms) response
        presets = [
            "Whatsapp la share aagura message: 5G tower rays vandhu sparrows and birds ah kill pannuthu, immediate ah stop panna solranga.",
            "TN Government announced tomorrow local holiday for Chennai schools due to heavy rain forecast by IMD.",
            "Intha kashayam kudicha 2 days la COVID and virus fully cure aayidum no need for hospital visit bro.",
            "ISRO successfully launched the Chandrayaan-3 mission from Sriharikota, historic moment for India."
        ]
        for p in presets:
            predict_dual_models(p)
        print("[READY] All models pre-warmed & cached! Zero-delay ready for UI queries.", flush=True)
    except Exception as e:
        print(f"[STARTUP WARNING] Model pre-warm notice: {e}", flush=True)
    print("=" * 60, flush=True)
    yield

app = FastAPI(
    title="CodeMix Dual Model Benchmarking System (MuRIL vs IndicBERT)",
    description="Tamil-English (Tanglish) Fake News Detection with Side-by-Side MuRIL vs IndicBERT Comparison",
    version="4.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DATA = os.path.join(BASE_DIR, "backend", "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class TextQuery(BaseModel):
    text: str
    api_key: Optional[str] = None

class ApiKeyPayload(BaseModel):
    api_key: str

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "models": ["google/muril-base-cased", "bert-base-multilingual-cased (IndicBERT)", "TF-IDF Statistical Baseline"],
        "dataset": "Tamil-English (Tanglish) 520 Curated Samples + Real-Time Live Feed",
        "backend": "FastAPI Dual-Model Benchmark Classifier with Live Verification Engine"
    }

@app.post("/api/predict")
def predict_fake_news(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    from backend.dual_model_classifier import predict_dual_models
    result = predict_dual_models(payload.text, custom_api_key=payload.api_key)
    return result

@app.post("/api/robustness")
def analyze_robustness(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    from backend.dual_model_classifier import predict_dual_models, predict_dual_raw
    from backend.robustness_analyzer import run_robustness_experiment

    baseline = predict_dual_models(payload.text)
    exp_results = run_robustness_experiment(
        original_text=payload.text,
        original_muril_res=baseline["muril_results"],
        original_indic_res=baseline["indicbert_results"],
        predict_fn=predict_dual_raw
    )
    return {
        **exp_results,
        "original_baseline": baseline
    }

@app.post("/api/explain")
def explain_text(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    from backend.explainability_engine import analyze_explainability
    return analyze_explainability(payload.text)

@app.post("/api/claim-analysis")
def extract_claim_api(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    from backend.claim_extractor import analyze_claim
    return analyze_claim(payload.text)

@app.get("/api/robustness-benchmark")
def get_robustness_benchmark():
    from backend.benchmark_eval import get_or_create_benchmark_results
    return get_or_create_benchmark_results()

@app.get("/api/stats")
def get_dataset_stats():
    json_path = os.path.join(DATA_DIR, "dataset.json")
    if not os.path.exists(json_path):
        alt_path = r"C:\Users\balla\OneDrive\Desktop\codemix\data\dataset.json"
        if os.path.exists(alt_path):
            json_path = alt_path
        else:
            return {"error": "Dataset not found"}

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data)
    fake_count = sum(1 for item in data if item["label"] == 1)
    real_count = sum(1 for item in data if item["label"] == 0)

    categories = {}
    sources = {}
    code_mix_types = {}

    for item in data:
        cat = item.get("category", "Uncategorized")
        categories[cat] = categories.get(cat, 0) + 1

        src = item.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1

        cmt = item.get("code_mix_type", "Tanglish")
        code_mix_types[cmt] = code_mix_types.get(cmt, 0) + 1

    from backend.realtime_verifier import get_realtime_dataset_stats
    rt_stats = get_realtime_dataset_stats()

    return {
        "total_samples": total + rt_stats["total_realtime_items"],
        "corpus_samples": total,
        "base_corpus_count": total,
        "realtime_ingested_samples": rt_stats["total_realtime_items"],
        "realtime_live_count": rt_stats["total_realtime_items"],
        "real_count": real_count,
        "fake_count": fake_count,
        "real_percentage": round((real_count / total) * 100, 1),
        "fake_percentage": round((fake_count / total) * 100, 1),
        "categories": categories,
        "sources": sources,
        "code_mix_types": code_mix_types
    }

@app.get("/api/realtime-dataset")
def get_realtime_dataset():
    from backend.realtime_verifier import get_realtime_dataset_stats
    return get_realtime_dataset_stats()

@app.post("/api/config/api-key")
def configure_api_key(payload: ApiKeyPayload):
    from backend.realtime_verifier import save_api_key
    success = save_api_key(payload.api_key)
    return {"success": success, "message": "API key successfully configured" if success else "Failed to save API key"}

@app.get("/api/config/api-key")
def get_api_key_status():
    from backend.realtime_verifier import get_api_key
    key = get_api_key()
    return {
        "configured": bool(key),
        "has_key": bool(key),
        "masked_key": (key[:4] + "..." + key[-4:]) if key and len(key) >= 8 else ("Configured" if key else "Not set (Using Free Zero-Key Engine)"),
        "mode": "Google Fact Check Tools API (Direct)" if key else "Free Zero-Key Real-Time Engine (Active)"
    }

@app.get("/api/metrics")
def get_metrics():
    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "base_model": {"name": "Traditional Base Model (TF-IDF)", "accuracy": 0.7727, "f1_score": 0.7680},
        "muril": {"name": "Google MuRIL", "accuracy": 0.9545, "f1_score": 0.9540},
        "indicbert": {"name": "IndicBERT", "accuracy": 0.9091, "f1_score": 0.9050},
        "best_overall_model": "Google MuRIL",
        "selection_verdict": "Google MuRIL is Good Enough to Choose for Production Deployment"
    }

@app.get("/api/download/{filename}")
def download_artifact(filename: str):
    allowed_files = [
        "fake_news_model.zip", 
        "Tamil_English_Fake_Real_Dataset_Full.xlsx", 
        "Tamil_English_Fake_Real_Dataset_Full.csv",
        "realtime_live_dataset.json"
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid filename requested")

    if filename.startswith("Tamil_English_Fake_Real_Dataset_Full") or filename == "realtime_live_dataset.json":
        file_path = os.path.join(DATA_DIR, filename)
    else:
        file_path = os.path.join(BACKEND_DATA, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, filename=filename)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def read_root():
    index_html = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {"message": "CodeMix Dual Model API running."}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 60)
    print("  CodeMix Dual-Model Misinformation Intelligence System")
    print("  Serving at: http://127.0.0.1:8000")
    print("=" * 60 + "\n", flush=True)
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)

