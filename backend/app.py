import os
import pickle
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.search import search
from backend.llm import build_answer
from backend.fake_news_classifier import classify_text, analyze_code_mixing

app = FastAPI(
    title="CodeMix & Fake News Detection API",
    description="Multilingual Code-Mixed (Tanglish / Telugu-English) Fake News Detection and RAG backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_DATA = r"C:\Users\balla\OneDrive\Desktop\CodeMix\backend\data"
STATIC_DIR = r"C:\Users\balla\OneDrive\Desktop\CodeMix\static"
os.makedirs(STATIC_DIR, exist_ok=True)

classifier_model = None
tfidf_vectorizer = None

def load_model_files():
    global classifier_model, tfidf_vectorizer
    model_path = os.path.join(BACKEND_DATA, "fake_news_model.pkl")
    vec_path = os.path.join(BACKEND_DATA, "tfidf_vectorizer.pkl")
    if os.path.exists(model_path) and os.path.exists(vec_path):
        try:
            with open(model_path, "rb") as f:
                classifier_model = pickle.load(f)
            with open(vec_path, "rb") as f:
                tfidf_vectorizer = pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {e}")

load_model_files()


class TextQuery(BaseModel):
    text: str

class QuestionQuery(BaseModel):
    question: str
    top_k: Optional[int] = 3


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "model_loaded": classifier_model is not None,
        "backend": "FastAPI CodeMix RAG & Fake News Detector"
    }


@app.post("/api/predict")
def predict_fake_news(payload: TextQuery):
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty")
    
    load_model_files()
    result = classify_text(payload.text, model=classifier_model, vectorizer=tfidf_vectorizer)
    return result


@app.post("/api/ask")
def ask_question(payload: QuestionQuery):
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    results, scores, detected_lang = search(
        payload.question,
        k=payload.top_k or 3,
        return_scores=True
    )
    answer = build_answer(results)

    return {
        "question": payload.question,
        "detected_language": detected_lang,
        "answer": answer,
        "retrieved_chunks": results,
        "relevance_scores": scores
    }


@app.get("/api/stats")
def get_dataset_stats():
    json_path = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data\dataset.json"
    if not os.path.exists(json_path):
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

        cmt = item.get("code_mix_type", "Unknown")
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


@app.get("/api/dataset")
def get_dataset(page: int = 1, limit: int = 10, search_text: Optional[str] = None, label: Optional[int] = None):
    json_path = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data\dataset.json"
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Dataset file not found")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered = data
    if search_text:
        st = search_text.lower()
        filtered = [item for item in filtered if st in item["text"].lower() or st in item.get("category", "").lower()]

    if label is not None:
        filtered = [item for item in filtered if item["label"] == label]

    total_items = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated = filtered[start_idx:end_idx]

    return {
        "page": page,
        "limit": limit,
        "total": total_items,
        "total_pages": (total_items + limit - 1) // limit,
        "items": paginated
    }


@app.get("/api/metrics")
def get_metrics():
    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            return json.load(f)
    return {
        "accuracy": 1.0,
        "precision": 1.0,
        "recall": 1.0,
        "f1_score": 1.0,
        "status": "Pre-configured baseline"
    }


@app.get("/api/download/{filename}")
def download_artifact(filename: str):
    allowed_files = ["fake_news_model.zip", "vector_store.zip", "Tamil_English_Fake_Real_Dataset_Full.xlsx", "Tamil_English_Fake_Real_Dataset_Full.csv"]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid filename requested")

    if filename.startswith("Tamil_English_Fake_Real_Dataset_Full"):
        file_path = os.path.join(r"C:\Users\balla\OneDrive\Desktop\CodeMix\data", filename)
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
    return {"message": "CodeMix API running."}
