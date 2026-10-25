# CodeMix — Explainable & Robustness-Aware Misinformation Intelligence System for Tamil-English (Tanglish)
### Comparative Transformer Benchmarking: Google MuRIL vs. IndicBERT / mBERT with Perturbation Robustness Analysis

An advanced AI-powered Language Intelligence and Misinformation Detection Platform designed specifically for **Tamil-English (Tanglish)** code-mixed communication. Beyond traditional binary classification (*Real vs. Fake*), the platform provides **interpretable explainability analysis**, **propositional claim extraction**, **multi-transformer decision reliability**, a transparent **Misinformation Risk Score**, and an empirical **Tanglish Robustness Lab** that systematically measures model resilience under natural phonetic, transliteration, orthographic, and code-mixing variations.

---

## 🔬 Academic Research Contribution

Conventional fake-news classification systems treat language models as black-box predictors, reporting high accuracy on static test sets while ignoring the realities of code-mixed social media communication. In real-world Tanglish (Romanized Tamil mixed with English), users employ informal transliterations, non-standard phonetic spellings, conversational slang, character elongation, and dialectal variations that degrade NLP tokenizer representations.

This project delivers **7 Core Research Contributions**:

1. **Tamil-English Code-Mixed Misinformation Classification**: Specialized dual-pipeline detection targeting low-resource, non-standardized Tanglish news and viral WhatsApp rumors.
2. **Comparative Multilingual Transformer Representations**: Side-by-side empirical evaluation of **Google MuRIL (`google/muril-base-cased`)** (pre-trained on 17 Indic languages and Romanized/transliterated Indic text) versus **IndicBERT / mBERT (`bert-base-multilingual-cased`)** (trained across 104 languages).
3. **Interpretable Explainability Engine**: Decouples model probability from transparent linguistic evidence across 13 distinct suspicious marker categories (sensationalism, artificial urgency, miracle health hoaxes, financial coercion, phishing triggers, conspiracy theories, and authority impersonation).
4. **Inter-Model Agreement & Decision Reliability**: Diagnoses inter-model concordance (*HIGH AGREEMENT*, *PARTIAL AGREEMENT / DISAGREEMENT*, *LOW CONFIDENCE*) and outputs a calibrated `Decision Reliability` rating (`HIGH`, `MEDIUM`, `LOW`), preventing misleading overconfidence near decision boundaries.
5. **Tanglish-Specific Robustness Evaluation (Primary Novelty ⭐)**: Introduces a controlled perturbation framework that generates natural, meaning-preserving Tanglish variants and evaluates whether transformer representations remain stable or flip under linguistic stress.
6. **Transparent Mathematical Misinformation Risk Scoring**: Formulates an interpretable multi-factor risk score ($0-100$) combining model evidence ensemble, consensus agreement, linguistic threat density, and perturbation stability.
7. **Production-Ready FastAPI Architecture**: Fully reproducible, zero-cost, lightweight modular architecture complete with interactive glassmorphic research studio and REST endpoints.

> ### 💡 Key Viva Defense: What is unique about your project?
> *"Unlike conventional fake news classifiers that output a single Real/Fake label with uncalibrated confidence on static text, our system investigates **linguistic explainability, transformer consensus, and perturbation robustness**. Most importantly, through our **Tanglish Robustness Analyzer**, we empirically prove that while IndicBERT achieves high accuracy on standard test samples, its predictions degrade under colloquial Tanglish spelling shifts. In contrast, Google MuRIL demonstrates superior stability due to its specialized Romanized Indic pre-training corpus."*

---

## 📐 Mathematical & Algorithmic Formulations

### 1. Tanglish Robustness Score
Given an original Tanglish input $x_0$ and a set of $N$ meaning-preserving natural variations $\{x_1, x_2, \dots, x_N\}$ generated across phonetic, transliteration, and lexical dimensions:

$$\text{Stability}_m = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}\left(\hat{y}_m(x_i) = \hat{y}_m(x_0)\right) \times 100$$

$$\text{Robustness Score} = \frac{\text{Stability}_{\text{MuRIL}} + \text{Stability}_{\text{IndicBERT}}}{2}$$

where $\mathbb{I}(\cdot)$ is the indicator function and $\hat{y}_m(x)$ is the predicted class label by model $m$.

### 2. Misinformation Risk Score
A transparent, interpretable linear combination on a $0 - 100$ scale:

$$\text{Risk Score} = \left\lfloor 0.40 \cdot E_{\text{model}} + 0.25 \cdot E_{\text{agreement}} + 0.20 \cdot E_{\text{signals}} + 0.15 \cdot E_{\text{robustness}} \right\rceil$$

- **$E_{\text{model}}$ (40%)**: Ensemble model probability that content is Fake: $\frac{P_{\text{fake}}^{\text{MuRIL}} + P_{\text{fake}}^{\text{IndicBERT}}}{2} \times 100$.
- **$E_{\text{agreement}}$ (25%)**: Consensus multiplier ($100$ if both models predict Fake; $50$ in case of disagreement; $0$ if both predict Real).
- **$E_{\text{signals}}$ (20%)**: Normalized severity density of detected rule-based linguistic threat indicators.
- **$E_{\text{robustness}}$ (15%)**: Perturbation persistence factor (measures whether misinformation signals withstand linguistic variation).

---

## 🌟 Comprehensive System Modules

| Module | Location | Purpose |
| :--- | :--- | :--- |
| **Explainability Engine** | `backend/explainability_engine.py` | Detects 13+ linguistic markers; distinguishes model predictions from rule-based evidence |
| **Claim Extraction Engine** | `backend/claim_extractor.py` | Strips viral framing; extracts core proposition, domain, and causal indicators |
| **Robustness Analyzer** | `backend/robustness_analyzer.py` | Generates 8 semantic Tanglish perturbations; computes stability rates and confidence shifts |
| **Agreement Engine** | `backend/agreement_engine.py` | Diagnoses model concordance and outputs calibrated Decision Reliability (`HIGH`, `MEDIUM`, `LOW`) |
| **Risk Scoring Engine** | `backend/risk_score.py` | Calculates transparent composite Misinformation Risk Score ($0-100$) with sub-factor breakdown |
| **Benchmark Evaluator** | `backend/benchmark_eval.py` | Implements Standard vs. Robustness metrics and 3-Way Linguistic Shift Experiment |
| **Dual Model Pipeline** | `backend/dual_model_classifier.py` | Feature extraction (768-dim) using MuRIL and IndicBERT with calibrated classification heads |
| **FastAPI REST Server** | `backend/app.py` | High-throughput asynchronous backend exposing full intelligence endpoints |
| **Research Dashboard** | `static/index.html`, `static/app.js` | Interactive web studio with Live Predictor, Tanglish Robustness Lab, and Benchmark Analytics |

---

## 📁 Repository Structure

```
CodeMix/
├── backend/
│   ├── __init__.py
│   ├── app.py                      # FastAPI REST server with all intelligence endpoints
│   ├── dual_model_classifier.py    # MuRIL & IndicBERT dual pipeline & CMI calculation
│   ├── explainability_engine.py    # 13-signal interpretable linguistic analysis
│   ├── claim_extractor.py          # Propositional claim extraction & causal indicator detection
│   ├── agreement_engine.py         # Inter-model consensus & decision reliability
│   ├── robustness_analyzer.py      # Tanglish perturbation generator & stability evaluator
│   ├── risk_score.py               # Transparent composite Misinformation Risk Score
│   ├── benchmark_eval.py           # Standard vs Robustness metrics & 3-way experiment
│   └── data/
│       ├── evaluation_metrics.json # Side-by-side accuracy, precision, recall, and F1-score
│       ├── muril_classifier.pkl     # Trained MuRIL calibrated classification head
│       ├── indicbert_classifier.pkl # Trained IndicBERT calibrated classification head
│       ├── robustness_benchmark_results.json # Cached empirical perturbation benchmark
│       └── fake_news_model.zip     # Compressed model package for distribution
├── data/
│   ├── Tamil_English_Fake_Real_Dataset_Full.csv   # Full 220-item dataset CSV
│   ├── Tamil_English_Fake_Real_Dataset_Full.xlsx  # Excel spreadsheet
│   └── dataset.json                               # Structured JSON dataset
├── static/
│   ├── index.html                  # Glassmorphism research studio with Robustness Lab
│   ├── style.css                   # Custom CSS styling tokens & responsive layouts
│   └── app.js                      # Modular frontend event handlers & API fetchers
├── build_dataset.py                # Dataset builder script
├── train_comparison_models.py      # Dual-model training and evaluation script
├── test_new_engines.py             # Unit tests for intelligence engines
├── test_full_inference.py          # End-to-end transformer inference test
├── test_api.py                     # FastAPI endpoint test client
├── requirements.txt                # Project dependencies
└── README.md                       # Comprehensive research documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository & Setup Python Environment
```bash
git clone https://github.com/Satya23BDS0326/codemix.git
cd CodeMix
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Verify Backend Engines & Endpoints
```bash
python test_new_engines.py
python test_api.py
```

### 4. Run Application Server
```bash
python -m uvicorn backend.app:app --reload --port 8000
```
Open **`http://127.0.0.1:8000`** in your browser.

---

## 📡 REST API Reference

### `POST /api/predict`
Executes dual-model inference, claim extraction, explainability analysis, model agreement, and transparent risk scoring.

**Request Body**:
```json
{
  "text": "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu, immediate ah stop panna solranga."
}
```

**Response**:
```json
{
  "best_model_recommendation": {
    "model_name": "Google MuRIL",
    "predicted_label": "Fake",
    "confidence": 99.9
  },
  "decision_reliability": "HIGH",
  "agreement_analysis": {
    "labels_agree": true,
    "agreement_state": "HIGH_AGREEMENT",
    "headline": "High Inter-Model Consensus"
  },
  "risk_score_analysis": {
    "final_risk_score": 91,
    "risk_level": "CRITICAL",
    "breakdown": {
      "model_evidence": 99.1,
      "model_agreement": 100.0,
      "risk_signals": 73.0,
      "robustness": 87.5
    }
  },
  "claim_analysis": {
    "formal_claim_statement": "5G tower electromagnetic radiation is causing sparrows and avian deaths.",
    "claim_type": "Technology / Environmental",
    "is_causal_claim": true
  },
  "explainability": {
    "signals_count": 3,
    "signals": [
      { "category": "Urgency & Fear", "severity": "HIGH", "name": "Artificial Urgency / Panic Induction" },
      { "category": "Conspiracy / Tech Hoax", "severity": "HIGH", "name": "Technological or Scientific Pseudofact" }
    ]
  }
}
```

### `POST /api/robustness`
Generates natural Tanglish variations, runs both models across all variations, and computes robustness metrics.

### `POST /api/explain`
Deep linguistic inspection returning detected suspicious signals and evidence tokens.

### `POST /api/claim-analysis`
Isolates central proposition, domain, and causal indicators.

### `GET /api/robustness-benchmark`
Returns pre-computed Standard vs. Robustness metrics and 3-Way Linguistic Shift experiment.

---

## 📊 Standard Performance vs. Tanglish Robustness Benchmark

| Evaluation Metric | Google MuRIL (`google/muril-base-cased`) | IndicBERT (`bert-base-multilingual-cased`) | Leader / Analysis |
| :--- | :---: | :---: | :--- |
| **Standard Accuracy** | 93.2% | 100.0% | IndicBERT (+6.8%) |
| **Precision (Fake Class)** | 100.0% | 100.0% | Tie (100.0%) |
| **Recall (Fake Class)** | 86.4% | 100.0% | IndicBERT (+13.6%) |
| **F1-Score** | 92.7% | 100.0% | IndicBERT (+7.3%) |
| **Tanglish Perturbation Stability ⭐** | **91.8%** | **81.4%** | **Google MuRIL (+10.4% ⭐)** |
| **Inter-Model Agreement Rate** | 86.4% | 86.4% | 38/44 Test Samples Agree |
| **Average Confidence Shift ($\Delta$)** | **4.2%** | **9.8%** | **Google MuRIL (2.3x more stable)** |
| **Maximum Confidence Drop** | **11.6%** | **24.3%** | **Google MuRIL (Resistant to catastrophic drops)** |
| **Transliteration Sensitivity** | **LOW** | **MEDIUM-HIGH** | **Google MuRIL** |

---

## 🧪 3-Way Linguistic Shift Experiment

Tracks prediction consistency and confidence decay as text transitions across progressive linguistic regimes:

1. **Group A: Standard English News Phrasing**: Canonical word order; 0% CMI; MuRIL: 95.5% Acc, IndicBERT: 97.7% Acc.
2. **Group B: Natural Tanglish (Code-Mixed)**: Mixed syntax; ~26.8% CMI; MuRIL: 93.2% Acc, IndicBERT: 100.0% Acc.
3. **Group C: Perturbed Tanglish (Spelling & Dialect Shifts)**: Phonetic transliteration shifts; MuRIL: 91.8% Stability, IndicBERT: 81.4% Stability.

> **Empirical Finding**: While IndicBERT exhibits higher accuracy on clean training text, its subword segmentation is brittle to Romanized phonetic variations. MuRIL maintains 91.8% stability due to its specialized Romanized Indic training corpus.

---

## 🎤 Viva Demonstration Walkthrough (2–3 Minutes)

Follow this structured workflow during project review:

1. **Input Submission**:
   - In **Live Predictor**, enter the benchmark case:
     `"Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu, immediate ah stop panna solranga."`
   - Click **Compare MuRIL vs IndicBERT**.
2. **Review Predictions & Consensus**:
   - Highlight that **both Google MuRIL (99.9%)** and **IndicBERT (98.3%)** evaluate the content as **FAKE**.
   - Point to the **Decision Reliability Badge**: `HIGH RELIABILITY (High Inter-Model Consensus)`.
3. **Present Claim Extraction**:
   - Show the **Extracted Core Proposition**: *"5G tower electromagnetic radiation is causing sparrows and avian deaths."*
   - Point out the identified Domain: `Technology / Environmental` and `Causal Assertion Flagged`.
4. **Explainable Suspicious Signals**:
   - Showcase the 3 flagged signals: *Artificial Urgency / Panic Induction* (`immediate ah`), *Social Media Chain Forwarding* (`whatsapp la share aagura`), and *Technological Hoax* (`5G tower rays`).
   - Highlight the **Distinction Note**: Model prediction is transformer-based, while linguistic evidence is transparent and rule-based.
5. **Transparent Misinformation Risk Score**:
   - Show **Misinformation Risk: 91 / 100 — CRITICAL**.
   - Walk the reviewer through the 4-part breakdown: Model Evidence (99.1), Model Agreement (100.0), Risk Signals (73.0), Robustness (87.5).
6. **Execute Tanglish Robustness Lab (Primary Novelty)**:
   - Click **"Test in Robustness Lab"** (or switch to the tab).
   - Click **Run Perturbation Experiment**.
   - Show the generated semantic variations:
     - *Spelling Variation*: `kathir vanthu ... kill panuthu`
     - *Transliteration Variation*: `aagudhu -> aaguthu`
     - *Lexical Substitution*: `kill pannuthu -> destroy pannuthu`
     - *Character Elongation*: `killll pannuthu`
     - *Punctuation Perturbation*: `!! Urgent forward!!`
     - *Common Abbreviation*: `whtsapp ... msg`
   - Review the **Variants Table**: Compare MuRIL vs IndicBERT stability and confidence shift.
   - Conclude with the **Research Observation**: MuRIL's Romanized pre-training makes it significantly more robust against real-world social media Tanglish noise.
