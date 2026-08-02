# CodeMix Backend — RAG for Code-Mixed (Telugu-English) Queries

A FastAPI RAG backend that answers questions over PDF content, built
to handle code-mixed Telugu-English queries (e.g. "AI jobs Hyderabad
lo unnaya") using MuRIL embeddings instead of an English-only model.

## What's in here

```
CodeMix/
├── backend/
│   ├── __init__.py
│   ├── retriever.py          # MuRIL embedding model (mean-pooled)
│   ├── language_detector.py  # detects en / te / code-mixed
│   ├── codemix.py            # query expansion + alignment normalization
│   ├── ingest.py             # PDF -> chunks -> FAISS (dense) + BM25 (sparse)
│   ├── search.py             # hybrid dense+sparse retrieval w/ query alignment
│   ├── llm.py                # packages top retrieved chunk as the answer (no generative model)
│   ├── app.py                # FastAPI app, exposes /ask
│   └── data/
│       ├── pdfs/             # put source PDFs here
│       └── vector_store/     # index.faiss, bm25.pkl, chunks.pkl land here
├── test_codemix.py
├── test_embedding.py
├── test_ingest.py
├── test_search.py
└── requirements.txt
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt --break-system-packages
```

(Drop `--break-system-packages` if you're inside a venv — it's only
needed on some Linux setups with an externally-managed Python.)

**No generative model is used anywhere in this project.** MuRIL is
the only model — it produces embeddings for retrieval. The "answer"
returned by `/ask` is the best-matching retrieved passage itself
(extractive), not a generated summary.

## Build the index

Put a PDF at `backend/data/pdfs/paper.pdf`, then from the project root:

```bash
python test_ingest.py
```

This builds both `index.faiss` (dense, MuRIL) and `bm25.pkl` (sparse)
inside `backend/data/vector_store/`.

## Run

```bash
uvicorn backend.app:app --reload
```

Then POST to `/ask`:
```bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d "{\"question\": \"AI jobs Hyderabad lo unnaya\"}"
```

Response includes the detected query language, the hybrid relevance
scores, the retrieved chunks, and a generated answer.

## Design notes (for the writeup)

- **Embedding model**: MuRIL (`google/muril-base-cased`), chosen over
  IndicBERT because it's trained on transliterated/romanized Indic
  text as well as native script — a direct match for code-mixed
  queries like the test case here.
- **Query alignment**: inspired by ContrastiveMix (Do et al., NAACL
  2024), which aligns code-mixed query embeddings toward their
  English-language counterpart via a contrastive loss during
  training. Without the infra to train a custom encoder, this project
  approximates the same effect at inference time: `codemix.py` strips
  Telugu function words from the query, `search.py` embeds both the
  original and cleaned versions and averages them.
- **Hybrid retrieval**: combines a BM25 sparse score with the MuRIL
  dense score, following the same paper's finding that sparse-dense
  hybrids outperform dense-only retrieval, especially for
  low-similarity language pairs.
