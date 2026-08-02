import os
import pickle
import json
import zipfile
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from rank_bm25 import BM25Okapi
import faiss

DATA_DIR = r"C:\Users\balla\OneDrive\Desktop\CodeMix\data"
BACKEND_DATA = r"C:\Users\balla\OneDrive\Desktop\CodeMix\backend\data"
VECTOR_STORE_DIR = os.path.join(BACKEND_DATA, "vector_store")
PUBLIC_VECTOR_DIR = os.path.join(r"C:\Users\balla\OneDrive\Desktop\CodeMix", "data", "vector_store")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKEND_DATA, exist_ok=True)
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(PUBLIC_VECTOR_DIR, exist_ok=True)

def train_fast():
    csv_file = os.path.join(DATA_DIR, "Tamil_English_Fake_Real_Dataset_Full.csv")
    df = pd.read_csv(csv_file)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)
    X = vectorizer.fit_transform(texts)
    y = np.array(labels)

    base_clf = LogisticRegression(C=2.5, max_iter=1000)
    model = CalibratedClassifierCV(estimator=base_clf, method='sigmoid')
    model.fit(X, y)

    y_pred = model.predict(X)

    acc = float(accuracy_score(y, y_pred))
    prec = float(precision_score(y, y_pred))
    rec = float(recall_score(y, y_pred))
    f1 = float(f1_score(y, y_pred))
    cm = confusion_matrix(y, y_pred).tolist()

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "confusion_matrix": cm,
        "total_samples": len(df)
    }

    metrics_path = os.path.join(BACKEND_DATA, "evaluation_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    model_path = os.path.join(BACKEND_DATA, "fake_news_model.pkl")
    vectorizer_path = os.path.join(BACKEND_DATA, "tfidf_vectorizer.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

    chunks = df.to_dict(orient="records")
    tokenized_corpus = [chunk["text"].lower().split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    bm25_path = os.path.join(VECTOR_STORE_DIR, "bm25.pkl")
    chunks_path = os.path.join(VECTOR_STORE_DIR, "chunks.pkl")

    with open(bm25_path, "wb") as f:
        pickle.dump(bm25, f)

    with open(chunks_path, "wb") as f:
        pickle.dump(chunks, f)

    dense_embeddings = X.toarray().astype("float32")
    norms = np.linalg.norm(dense_embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    dense_embeddings = dense_embeddings / norms

    dimension = dense_embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(dense_embeddings)

    faiss_path = os.path.join(VECTOR_STORE_DIR, "index.faiss")
    faiss.write_index(index, faiss_path)

    # Save to data/vector_store as well
    faiss.write_index(index, os.path.join(PUBLIC_VECTOR_DIR, "index.faiss"))
    with open(os.path.join(PUBLIC_VECTOR_DIR, "bm25.pkl"), "wb") as f:
        pickle.dump(bm25, f)
    with open(os.path.join(PUBLIC_VECTOR_DIR, "chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

    # Zip 1: fake_news_model.zip
    model_zip_path = os.path.join(BACKEND_DATA, "fake_news_model.zip")
    with zipfile.ZipFile(model_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(model_path, arcname="fake_news_model.pkl")
        zf.write(vectorizer_path, arcname="tfidf_vectorizer.pkl")
        zf.write(metrics_path, arcname="evaluation_metrics.json")
        zf.write(csv_file, arcname="Tamil_English_Fake_Real_Dataset_Full.csv")

    # Zip 2: vector_store.zip
    vector_zip_path = os.path.join(BACKEND_DATA, "vector_store.zip")
    with zipfile.ZipFile(vector_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(faiss_path, arcname="index.faiss")
        zf.write(bm25_path, arcname="bm25.pkl")
        zf.write(chunks_path, arcname="chunks.pkl")

    print("[SUCCESS] Fast training and vector store generation completed!", flush=True)

if __name__ == "__main__":
    train_fast()
