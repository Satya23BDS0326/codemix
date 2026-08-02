import fitz
import faiss
import numpy as np
import os
import pickle

from rank_bm25 import BM25Okapi

from backend.retriever import get_embedding

VECTOR_PATH = "data/vector_store"


def extract_text(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text


def chunk_text(text, size=500):

    chunks = []

    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])

    return chunks


def create_index(pdf_path):

    text = extract_text(pdf_path)

    chunks = chunk_text(text)

    # ---- Dense (MuRIL) index ----
    embeddings = np.array(
        [get_embedding(c) for c in chunks]
    ).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    os.makedirs(VECTOR_PATH, exist_ok=True)

    faiss.write_index(
        index,
        f"{VECTOR_PATH}/index.faiss"
    )

    # ---- Sparse (BM25) index ----
    # Simple whitespace tokenization is enough here since BM25 is only
    # used as one half of the hybrid score, not the sole retriever.
    tokenized_chunks = [c.lower().split() for c in chunks]

    bm25 = BM25Okapi(tokenized_chunks)

    with open(f"{VECTOR_PATH}/bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)

    # ---- Chunks (shared by both indexes) ----
    with open(f"{VECTOR_PATH}/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"Index Created ({len(chunks)} chunks, dense dim={dimension})")
