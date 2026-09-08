document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            navTabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetPane = document.getElementById(target);
            if (targetPane) targetPane.classList.add('active');

            if (target === 'tab-analytics') {
                loadAnalytics();
            } else if (target === 'tab-artifacts') {
                loadMetrics();
            }
        });
    });

    // Elements
    const detectorInput = document.getElementById('detector-input');
    const btnClear = document.getElementById('btn-clear');
    const btnAnalyze = document.getElementById('btn-analyze');
    const presetBtns = document.querySelectorAll('.preset-btn');
    const charWordCount = document.getElementById('char-word-count');

    const resultEmpty = document.getElementById('result-empty');
    const resultDetails = document.getElementById('result-details');

    const bestModelName = document.getElementById('best-model-name');
    const bestModelReason = document.getElementById('best-model-reason');
    const bestVerdictTitle = document.getElementById('best-verdict-title');

    const murilBanner = document.getElementById('muril-banner');
    const murilIcon = document.getElementById('muril-icon');
    const murilTitle = document.getElementById('muril-title');
    const murilSubtitle = document.getElementById('muril-subtitle');
    const murilProbs = document.getElementById('muril-probs');

    const indicBanner = document.getElementById('indic-banner');
    const indicIcon = document.getElementById('indic-icon');
    const indicTitle = document.getElementById('indic-title');
    const indicSubtitle = document.getElementById('indic-subtitle');
    const indicProbs = document.getElementById('indic-probs');

    const resLangType = document.getElementById('res-lang-type');
    const resCmi = document.getElementById('res-cmi');
    const resCategory = document.getElementById('res-category');
    const resRatio = document.getElementById('res-ratio');

    // Live Word & Character Counter
    function updateCounter() {
        if (!charWordCount || !detectorInput) return;
        const text = detectorInput.value.trim();
        const chars = detectorInput.value.length;
        const words = text ? text.split(/\s+/).length : 0;
        charWordCount.innerText = `${words} words · ${chars} chars`;
    }

    if (detectorInput) {
        detectorInput.addEventListener('input', updateCounter);
        // Ctrl + Enter shortcut
        detectorInput.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                const text = detectorInput.value.trim();
                if (text) runDualAnalysis(text);
            }
        });
    }

    // Benchmark Presets
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!btn.dataset.preset) return;
            detectorInput.value = btn.dataset.preset;
            updateCounter();
            runDualAnalysis(btn.dataset.preset);
        });
    });

    // Clear Button
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            detectorInput.value = '';
            updateCounter();
            if (resultEmpty) resultEmpty.classList.remove('hidden');
            if (resultDetails) resultDetails.classList.add('hidden');
        });
    }

    // Analyze Button
    if (btnAnalyze) {
        btnAnalyze.addEventListener('click', () => {
            const text = detectorInput.value.trim();
            if (text) {
                runDualAnalysis(text);
            } else {
                detectorInput.focus();
            }
        });
    }

    // Dual Model API Inference
    async function runDualAnalysis(text) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing Dual Inference...';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!res.ok) throw new Error('API request failed');

            const data = await res.json();
            renderDualResults(data);
        } catch (err) {
            console.error('Error analyzing text:', err);
            alert('Error connecting to backend API. Please make sure the server is running.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<i class="fa-solid fa-code-compare"></i> Compare MuRIL vs IndicBERT';
        }
    }

    // Render Dual Model Results
    function renderDualResults(data) {
        if (resultEmpty) resultEmpty.classList.add('hidden');
        if (resultDetails) {
            resultDetails.classList.remove('hidden');
            // Smooth scroll into view
            resultDetails.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Winner Recommendation
        const rec = data.best_model_recommendation;
        if (bestModelName) bestModelName.innerText = rec.model_name;
        if (bestModelReason) bestModelReason.innerText = rec.reason;
        if (bestVerdictTitle) {
            bestVerdictTitle.innerText = rec.predicted_label.toUpperCase();
            bestVerdictTitle.style.color = rec.predicted_label === 'Fake' ? 'var(--verdict-fake)' : 'var(--verdict-real)';
        }

        // MuRIL Card
        const m = data.muril_results;
        const isFakeM = m.label === 1;
        if (murilBanner) murilBanner.className = `verdict-banner ${isFakeM ? 'fake' : 'real'}`;
        if (murilIcon) murilIcon.innerHTML = isFakeM ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        if (murilTitle) murilTitle.innerText = m.label_name;
        if (murilSubtitle) murilSubtitle.innerText = `Confidence: ${m.confidence}%`;
        if (murilProbs) murilProbs.innerText = `Real: ${(m.probabilities.Real * 100).toFixed(1)}% | Fake: ${(m.probabilities.Fake * 100).toFixed(1)}%`;

        // IndicBERT Card
        const ind = data.indicbert_results;
        const isFakeI = ind.label === 1;
        if (indicBanner) indicBanner.className = `verdict-banner ${isFakeI ? 'fake' : 'real'}`;
        if (indicIcon) indicIcon.innerHTML = isFakeI ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        if (indicTitle) indicTitle.innerText = ind.label_name;
        if (indicSubtitle) indicSubtitle.innerText = `Confidence: ${ind.confidence}%`;
        if (indicProbs) indicProbs.innerText = `Real: ${(ind.probabilities.Real * 100).toFixed(1)}% | Fake: ${(ind.probabilities.Fake * 100).toFixed(1)}%`;

        // Linguistic Analysis
        if (resLangType) resLangType.innerText = data.code_mix_type;
        if (resCmi) resCmi.innerText = `${data.cmi}%`;
        if (resCategory) resCategory.innerText = data.category;
        if (resRatio) resRatio.innerText = `${data.tanglish_pct}% / ${data.english_pct}%`;

        // AI Summary & Credibility Assessment
        const aiSummaryEl = document.getElementById('res-ai-summary');
        if (aiSummaryEl) {
            aiSummaryEl.innerHTML = data.ai_summary || `<strong>${rec.predicted_label === 'Fake' ? '⚠️ Misinformation Risk Detected:' : '✅ Credible Content Verified:'}</strong> ${rec.reason}`;
        }

        const riskListEl = document.getElementById('res-risk-list');
        if (riskListEl) {
            riskListEl.innerHTML = '';
            if (data.risk_factors && data.risk_factors.length > 0) {
                data.risk_factors.forEach(rf => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${rf}`;
                    riskListEl.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.style.background = 'rgba(16, 185, 129, 0.08)';
                li.style.borderColor = 'rgba(16, 185, 129, 0.25)';
                li.style.color = '#34D399';
                li.innerHTML = `<i class="fa-solid fa-circle-check" style="color:#10B981"></i> Standard journalistic phrasing with no high-risk sensationalist markers detected`;
                riskListEl.appendChild(li);
            }
        }
    }

    // Benchmark Analytics
    async function loadAnalytics() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();

            const srcChart = document.getElementById('source-chart');
            if (srcChart && data.sources) {
                srcChart.innerHTML = '';
                const total = data.total_samples;
                Object.entries(data.sources).sort((a,b) => b[1] - a[1]).forEach(([src, count]) => {
                    const pct = Math.round((count / total) * 100);
                    srcChart.innerHTML += `
                        <div class="chart-bar-item">
                            <div class="bar-meta">
                                <span>${src}</span>
                                <span style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${count} items (${pct}%)</span>
                            </div>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: ${pct}%; background: linear-gradient(90deg, #6366F1, #2DD4BF);"></div>
                            </div>
                        </div>
                    `;
                });
            }
        } catch (err) {
            console.error('Analytics load error:', err);
        }
    }

    // Model Performance Metrics
    async function loadMetrics() {
        try {
            const res = await fetch('/api/metrics');
            const data = await res.json();

            if (data.muril) {
                const el = document.getElementById('bm-muril-acc');
                if (el) el.innerText = `${(data.muril.accuracy * 100).toFixed(1)}%`;
            }
            if (data.indicbert) {
                const el = document.getElementById('bm-indic-acc');
                if (el) el.innerText = `${(data.indicbert.accuracy * 100).toFixed(1)}%`;
            }
        } catch (err) {
            console.error('Metrics load error:', err);
        }
    }
});
