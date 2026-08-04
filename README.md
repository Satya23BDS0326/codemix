# CodeMix — Tamil-English (Tanglish) Fake News Detection Platform
### Side-by-Side Model Benchmarking: Google MuRIL vs. IndicBERT

An AI-powered Fake News Detection and Language Intelligence Platform designed specifically for **Tamil-English (Tanglish)** code-mixed content. The platform evaluates news text, social media posts, and viral WhatsApp messages simultaneously using two state-of-the-art multilingual transformer encoders: **Google MuRIL (`google/muril-base-cased`)** and **IndicBERT (`bert-base-multilingual-cased`)**, automatically recommending the best model based on classification confidence.

---

## 🌟 Key Features

1. **Dual Transformer Benchmarking**:
   - **Google MuRIL** (`google/muril-base-cased`): Pre-trained on 17 Indic languages and transliterated / romanized Indic text.
   - **IndicBERT / mBERT** (`bert-base-multilingual-cased`): Multilingual BERT architecture trained on 104 languages.
   - **Side-by-Side Comparison**: Computes classification verdicts (REAL vs. FAKE), confidence percentages, and class probability distributions for both models.
2. **Code-Mixing Analysis (CMI)**:
   - Calculates the **Code-Mixing Index (CMI)**, Tanglish percentage, and English percentage in real-time.
3. **Automated Misinformation Risk Factor Detection**:
   - Detects health hoax remedies, phishing download links, radiation/5G conspiracy theories, and viral forward chain phrasing.
4. **Dataset & Metrics Dashboard**:
   - 220 balanced Tamil-English news dataset entries.
   - Real-time statistics, category distribution, rumor source breakdown, and model evaluation metrics (Accuracy, F1-Score, Precision, Recall, Confusion Matrix).
5. **One-Click Downloads**:
   - Export trained model packages (`fake_news_model.zip`) and full Excel datasets (`Tamil_English_Fake_Real_Dataset_Full.xlsx`).

---

## 📁 Repository Structure

```
CodeMix/
├── backend/
│   ├── __init__.py
│   ├── app.py                      # FastAPI server exposing endpoints and serving static UI
│   ├── dual_model_classifier.py    # Real-time MuRIL vs. IndicBERT inference and CMI analysis
│   └── data/
│       ├── evaluation_metrics.json # Side-by-side accuracy, precision, recall, and F1-score
│       ├── muril_classifier.pkl     # Trained MuRIL classifier head
│       ├── indicbert_classifier.pkl # Trained IndicBERT classifier head
│       └── fake_news_model.zip     # Compressed model package for distribution
├── data/
│   ├── Tamil_English_Fake_Real_Dataset_Full.csv   # Full 220-item dataset CSV
│   ├── Tamil_English_Fake_Real_Dataset_Full.xlsx  # Excel spreadsheet
│   └── dataset.json                               # Structured JSON dataset
├── static/
│   ├── index.html                  # Glassmorphism web dashboard UI
│   ├── style.css                   # Custom CSS styling tokens
│   └── app.js                      # Dynamic UI event handlers and API fetchers
├── build_dataset.py                # Dataset builder script
├── train_comparison_models.py      # Dual-model training and evaluation script
├── requirements.txt                # Project dependencies
└── README.md                       # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository & Create Virtual Environment
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

### 3. Generate Dataset & Train Models
```bash
python build_dataset.py
python train_comparison_models.py
```

### 4. Run Web Application Server
```bash
python -m uvicorn backend.app:app --reload --port 8000
```
Open **`http://127.0.0.1:8000`** in your web browser.

---

## 📡 API Documentation

### `POST /api/predict`
Analyzes a Tamil-English text string using both Google MuRIL and IndicBERT.

**Request Body**:
```json
{
  "text": "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu"
}
```

**Response**:
```json
{
  "text": "Whatsapp la share aagura message: 5G tower rays vandhu sparrows ah kill pannuthu",
  "category": "Tech Rumor",
  "code_mix_type": "Tanglish (Tamil-English)",
  "cmi": 30.8,
  "best_model_recommendation": {
    "model_name": "Google MuRIL",
    "predicted_label": "Fake",
    "confidence": 94.3,
    "reason": "Google MuRIL achieved higher confidence due to its specialized transliterated & romanized Indic pre-training."
  },
  "muril_results": {
    "model_name": "Google MuRIL (google/muril-base-cased)",
    "label": 1,
    "label_name": "Fake",
    "confidence": 94.3
  },
  "indicbert_results": {
    "model_name": "IndicBERT (bert-base-multilingual-cased)",
    "label": 1,
    "label_name": "Fake",
    "confidence": 88.2
  }
}
```

### `GET /api/stats`
Returns dataset distribution across categories, sources, and code-mixed language types.

### `GET /api/metrics`
Returns accuracy, precision, recall, and F1-score metrics for MuRIL vs. IndicBERT.

### `GET /api/download/{filename}`
Downloads artifact files (`fake_news_model.zip` or `Tamil_English_Fake_Real_Dataset_Full.xlsx`).

---

## 🔬 Model Evaluation Summary

| Model Architecture | Accuracy | Precision | Recall | F1 Score |
| :--- | :---: | :---: | :---: | :---: |
| **Google MuRIL (`google/muril-base-cased`)** | **90.0%** | **100.0%** | **80.0%** | **88.9%** |
| **IndicBERT (`bert-base-multilingual-cased`)** | **90.0%** | **100.0%** | **80.0%** | **88.9%** |

---
