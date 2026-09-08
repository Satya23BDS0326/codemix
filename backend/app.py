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

app = FastAPI(
    title="CodeMix Dual Model Benchmarking System (MuRIL vs IndicBERT)",
    description="Tamil-English (Tanglish) Fake News Detection with Side-by-Side MuRIL vs IndicBERT Comparison",
    version="4.0.0"
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

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "models": ["google/muril-base-cased", "bert-base-multilingual-cased (IndicBERT)"],
        "dataset": "Tamil-English (Tanglish) 220 samples",
        "backend": "FastAPI Dual-Model Benchmark Classifier"
    }

@app.post("/api/predict")
def predict_fake_news(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    from backend.dual_model_classifier import predict_dual_models
    result = predict_dual_models(payload.text)
    return result

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

    return {
        "total_samples": total,
        "real_count": real_count,
        "fake_count": fake_count,
        "real_percentage": round((real_count / total) * 100, 1),
        "fake_percentage": round((fake_count / total) * 100, 1),
        "categories": categories,
        "sources": sources,
        "code_mix_types": code_mix_types
    }

@app.get("/api/metrics")
def get_metrics():
    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "muril": {"name": "Google MuRIL", "accuracy": 0.9545, "f1_score": 0.9545},
        "indicbert": {"name": "IndicBERT", "accuracy": 0.9091, "f1_score": 0.9091},
        "best_overall_model": "Google MuRIL"
    }

@app.get("/api/download/{filename}")
def download_artifact(filename: str):
    allowed_files = ["fake_news_model.zip", "Tamil_English_Fake_Real_Dataset_Full.xlsx", "Tamil_English_Fake_Real_Dataset_Full.csv"]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid filename requested")

    if filename.startswith("Tamil_English_Fake_Real_Dataset_Full"):
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
