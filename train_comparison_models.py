import os
import pickle
import json
import zipfile
import torch
import pandas as pd
import numpy as np

from transformers import AutoTokenizer, AutoModel
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

DATA_DIR = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data"
BACKEND_DATA = r"C:\Users\balla\OneDrive\Desktop\CodeMix\backend\data"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA, exist_ok=True)

# 1. MuRIL Model
MURIL_NAME = "google/muril-base-cased"
print("Loading Google MuRIL Tokenizer and Model...", flush=True)
muril_tok = AutoTokenizer.from_pretrained(MURIL_NAME)
muril_mod = AutoModel.from_pretrained(MURIL_NAME)
muril_mod.eval()

# 2. IndicBERT / mBERT Model
INDIC_NAME = "bert-base-multilingual-cased"
print("Loading IndicBERT / mBERT Tokenizer and Model...", flush=True)
indic_tok = AutoTokenizer.from_pretrained(INDIC_NAME)
indic_mod = AutoModel.from_pretrained(INDIC_NAME)
indic_mod.eval()

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts

def get_muril_emb(text):
    inputs = muril_tok(text, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        output = muril_mod(**inputs)
    emb = mean_pooling(output, inputs["attention_mask"])
    return emb[0].cpu().numpy()

def get_indic_emb(text):
    inputs = indic_tok(text, padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.no_grad():
        output = indic_mod(**inputs)
    emb = mean_pooling(output, inputs["attention_mask"])
    return emb[0].cpu().numpy()

def train_and_compare():
    csv_file = os.path.join(DATA_DIR, "Tamil_English_Fake_Real_Dataset_Full.csv")
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Dataset CSV not found at {csv_file}")

    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} Tamil-English samples.", flush=True)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    print("Extracting MuRIL 768-dim Embeddings...", flush=True)
    muril_embs = [get_muril_emb(t) for t in texts]

    print("Extracting IndicBERT 768-dim Embeddings...", flush=True)
    indic_embs = [get_indic_emb(t) for t in texts]

    X_muril = np.array(muril_embs, dtype="float32")
    X_indic = np.array(indic_embs, dtype="float32")
    y = np.array(labels)

    X_train_m, X_test_m, y_train, y_test = train_test_split(X_muril, y, test_size=0.2, random_state=42, stratify=y)
    X_train_i, X_test_i, _, _ = train_test_split(X_indic, y, test_size=0.2, random_state=42, stratify=y)

    print("Training MuRIL Classifier...", flush=True)
    clf_muril = CalibratedClassifierCV(LogisticRegression(C=2.0, max_iter=1000), method='sigmoid')
    clf_muril.fit(X_train_m, y_train)
    y_pred_m = clf_muril.predict(X_test_m)

    acc_m = float(accuracy_score(y_test, y_pred_m))
    prec_m = float(precision_score(y_test, y_pred_m))
    rec_m = float(recall_score(y_test, y_pred_m))
    f1_m = float(f1_score(y_test, y_pred_m))
    cm_m = confusion_matrix(y_test, y_pred_m).tolist()

    print("Training IndicBERT Classifier...", flush=True)
    clf_indic = CalibratedClassifierCV(LogisticRegression(C=2.0, max_iter=1000), method='sigmoid')
    clf_indic.fit(X_train_i, y_train)
    y_pred_i = clf_indic.predict(X_test_i)

    acc_i = float(accuracy_score(y_test, y_pred_i))
    prec_i = float(precision_score(y_test, y_pred_i))
    rec_i = float(recall_score(y_test, y_pred_i))
    f1_i = float(f1_score(y_test, y_pred_i))
    cm_i = confusion_matrix(y_test, y_pred_i).tolist()

    print(f"\nModel Comparison Results:")
    print(f"  Google MuRIL: Acc={acc_m:.4f}, Prec={prec_m:.4f}, Rec={rec_m:.4f}, F1={f1_m:.4f}", flush=True)
    print(f"  IndicBERT:    Acc={acc_i:.4f}, Prec={prec_i:.4f}, Rec={rec_i:.4f}, F1={f1_i:.4f}", flush=True)

    metrics = {
        "dataset_name": "Tamil-English (Tanglish) Fake Real News",
        "total_samples": len(df),
        "muril": {
            "name": "Google MuRIL (google/muril-base-cased)",
            "accuracy": round(acc_m, 4),
            "precision": round(prec_m, 4),
            "recall": round(rec_m, 4),
            "f1_score": round(f1_m, 4),
            "confusion_matrix": cm_m
        },
        "indicbert": {
            "name": "IndicBERT / mBERT (bert-base-multilingual-cased)",
            "accuracy": round(acc_i, 4),
            "precision": round(prec_i, 4),
            "recall": round(rec_i, 4),
            "f1_score": round(f1_i, 4),
            "confusion_matrix": cm_i
        },
        "best_overall_model": "Google MuRIL" if f1_m >= f1_i else "IndicBERT"
    }

    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    with open(os.path.join(BACKEND_DATA, "muril_classifier.pkl"), "wb") as f:
        pickle.dump(clf_muril, f)

    with open(os.path.join(BACKEND_DATA, "indicbert_classifier.pkl"), "wb") as f:
        pickle.dump(clf_indic, f)

    # Zip artifact
    model_zip_path = os.path.join(BACKEND_DATA, "fake_news_model.zip")
    with zipfile.ZipFile(model_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(os.path.join(BACKEND_DATA, "muril_classifier.pkl"), arcname="muril_classifier.pkl")
        zf.write(os.path.join(BACKEND_DATA, "indicbert_classifier.pkl"), arcname="indicbert_classifier.pkl")
        zf.write(metrics_path, arcname="evaluation_metrics.json")
        zf.write(csv_file, arcname="Tamil_English_Fake_Real_Dataset_Full.csv")

    print("[SUCCESS] Dual Model Comparison Pipeline Trained and Saved!", flush=True)

if __name__ == "__main__":
    train_and_compare()
