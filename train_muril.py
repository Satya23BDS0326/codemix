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

MODEL_NAME = "google/muril-base-cased"
DATA_DIR = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data"
BACKEND_DATA = r"C:\Users\balla\OneDrive\Desktop\CodeMix\backend\data"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA, exist_ok=True)

print("Loading MuRIL Tokenizer and Model...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
muril_model = AutoModel.from_pretrained(MODEL_NAME)
muril_model.eval()

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts

def get_muril_embedding(text):
    inputs = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt"
    )
    with torch.no_grad():
        output = muril_model(**inputs)
    embedding = mean_pooling(output, inputs["attention_mask"])
    return embedding[0].cpu().numpy()

def train_muril_pipeline():
    print("Loading Tamil-English (Tanglish) Dataset...", flush=True)
    csv_file = os.path.join(DATA_DIR, "Tamil_English_Fake_Real_Dataset_Full.csv")
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Dataset CSV not found at {csv_file}")

    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} Tamil-English samples.", flush=True)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    print("Extracting MuRIL 768-dim Embeddings...", flush=True)
    embeddings = []
    for idx, text in enumerate(texts):
        emb = get_muril_embedding(text)
        embeddings.append(emb)

    X = np.array(embeddings, dtype="float32")
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training Calibrated Classifier on MuRIL Embeddings...", flush=True)
    base_clf = LogisticRegression(C=2.0, max_iter=1000)
    clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid')
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()

    print(f"MuRIL Evaluation Results: Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}", flush=True)

    metrics = {
        "model_architecture": "google/muril-base-cased (MuRIL)",
        "language_pair": "Tamil-English (Tanglish)",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "total_samples": len(df),
        "train_samples": len(y_train),
        "test_samples": len(y_test)
    }

    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    classifier_path = os.path.join(BACKEND_DATA, "muril_classifier.pkl")
    with open(classifier_path, "wb") as f:
        pickle.dump(clf, f)

    # Zip artifact: fake_news_model.zip
    model_zip_path = os.path.join(BACKEND_DATA, "fake_news_model.zip")
    with zipfile.ZipFile(model_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(classifier_path, arcname="muril_classifier.pkl")
        zf.write(metrics_path, arcname="evaluation_metrics.json")
        zf.write(csv_file, arcname="Tamil_English_Fake_Real_Dataset_Full.csv")

    print("[SUCCESS] Pure MuRIL Tamil-English Classifier Trained and Exported Successfully!", flush=True)

if __name__ == "__main__":
    train_muril_pipeline()
