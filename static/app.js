document.addEventListener('DOMContentLoaded', () => {
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;

            navTabs.forEach(t => t.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(target).classList.add('active');

            if (target === 'tab-analytics') {
                loadAnalytics();
            } else if (target === 'tab-artifacts') {
                loadMetrics();
            }
        });
    });

    const detectorInput = document.getElementById('detector-input');
    const btnClear = document.getElementById('btn-clear');
    const btnAnalyze = document.getElementById('btn-analyze');
    const presetBtns = document.querySelectorAll('.preset-btn');

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

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            detectorInput.value = btn.dataset.preset;
            runDualAnalysis(btn.dataset.preset);
        });
    });

    btnClear.addEventListener('click', () => {
        detectorInput.value = '';
        resultEmpty.classList.remove('hidden');
        resultDetails.classList.add('hidden');
    });

    btnAnalyze.addEventListener('click', () => {
        const text = detectorInput.value.trim();
        if (text) {
            runDualAnalysis(text);
        }
    });

    async function runDualAnalysis(text) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing MuRIL & IndicBERT...';

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
            alert('Error connecting to backend API.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<i class="fa-solid fa-code-compare"></i> Compare MuRIL vs IndicBERT';
        }
    }

    function renderDualResults(data) {
        resultEmpty.classList.add('hidden');
        resultDetails.classList.remove('hidden');

        // Winner model
        const rec = data.best_model_recommendation;
        bestModelName.innerText = rec.model_name;
        bestModelReason.innerText = rec.reason;
        bestVerdictTitle.innerText = rec.predicted_label;
        bestVerdictTitle.style.color = rec.predicted_label === 'Fake' ? '#F43F5E' : '#10B981';

        // MuRIL card
        const m = data.muril_results;
        const isFakeM = m.label === 1;
        murilBanner.className = `verdict-banner ${isFakeM ? 'fake' : 'real'}`;
        murilIcon.innerHTML = isFakeM ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        murilTitle.innerText = m.label_name;
        murilSubtitle.innerText = `Confidence: ${m.confidence}%`;
        murilProbs.innerText = `Real: ${(m.probabilities.Real * 100).toFixed(1)}% | Fake: ${(m.probabilities.Fake * 100).toFixed(1)}%`;

        // IndicBERT card
        const ind = data.indicbert_results;
        const isFakeI = ind.label === 1;
        indicBanner.className = `verdict-banner ${isFakeI ? 'fake' : 'real'}`;
        indicIcon.innerHTML = isFakeI ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        indicTitle.innerText = ind.label_name;
        indicSubtitle.innerText = `Confidence: ${ind.confidence}%`;
        indicProbs.innerText = `Real: ${(ind.probabilities.Real * 100).toFixed(1)}% | Fake: ${(ind.probabilities.Fake * 100).toFixed(1)}%`;

        // Tanglish breakdown
        resLangType.innerText = data.code_mix_type;
        resCmi.innerText = `${data.cmi}%`;
        resCategory.innerText = data.category;
        resRatio.innerText = `${data.tanglish_pct}% / ${data.english_pct}%`;
    }

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
                                <span style="font-family: 'JetBrains Mono', monospace;">${count} items (${pct}%)</span>
                            </div>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: ${pct}%; background: linear-gradient(90deg, #06B6D4, #10B981);"></div>
                            </div>
                        </div>
                    `;
                });
            }
        } catch (err) {
            console.error('Analytics load error:', err);
        }
    }

    async function loadMetrics() {
        try {
            const res = await fetch('/api/metrics');
            const data = await res.json();

            if (data.muril) {
                document.getElementById('bm-muril-acc').innerText = `${(data.muril.accuracy * 100).toFixed(1)}%`;
            }
            if (data.indicbert) {
                document.getElementById('bm-indic-acc').innerText = `${(data.indicbert.accuracy * 100).toFixed(1)}%`;
            }
        } catch (err) {
            console.error('Metrics load error:', err);
        }
    }
});
