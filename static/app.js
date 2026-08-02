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

    const verdictBanner = document.getElementById('verdict-banner');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictSubtitle = document.getElementById('verdict-subtitle');
    const gaugeFill = document.getElementById('gauge-fill');
    const gaugeScore = document.getElementById('gauge-score');

    const resLangType = document.getElementById('res-lang-type');
    const resCategory = document.getElementById('res-category');
    const resRatio = document.getElementById('res-ratio');
    const resRiskList = document.getElementById('res-risk-list');
    const resExplanation = document.getElementById('res-explanation');

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            detectorInput.value = btn.dataset.preset;
            runAnalysis(btn.dataset.preset);
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
            runAnalysis(text);
        }
    });

    async function runAnalysis(text) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> MuRIL Processing...';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!res.ok) throw new Error('API request failed');

            const data = await res.json();
            renderPredictionResult(data);
        } catch (err) {
            console.error('Error analyzing text:', err);
            alert('Error connecting to backend MuRIL API.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<i class="fa-solid fa-microchip"></i> Predict with MuRIL';
        }
    }

    function renderPredictionResult(data) {
        resultEmpty.classList.add('hidden');
        resultDetails.classList.remove('hidden');

        const isFake = data.label === 1;

        verdictBanner.className = `verdict-banner ${isFake ? 'fake' : 'real'}`;
        verdictIcon.innerHTML = isFake ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        verdictTitle.innerText = isFake ? 'FAKE NEWS' : 'VERIFIED REAL NEWS';
        verdictSubtitle.innerText = `MuRIL Confidence: ${data.confidence}%`;

        gaugeFill.style.width = `${data.confidence}%`;
        gaugeScore.innerText = `${Math.round(data.confidence)}%`;

        resLangType.innerText = `${data.code_mix_type}`;
        resCategory.innerText = data.category;
        resRatio.innerText = `${data.tanglish_pct}% / ${data.english_pct}%`;

        resRiskList.innerHTML = '';
        if (data.risk_factors && data.risk_factors.length > 0) {
            data.risk_factors.forEach(risk => {
                const li = document.createElement('li');
                li.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${risk}`;
                resRiskList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.style.background = 'rgba(16, 185, 129, 0.1)';
            li.style.borderColor = 'rgba(16, 185, 129, 0.3)';
            li.style.color = '#6EE7B7';
            li.innerHTML = `<i class="fa-solid fa-shield-check"></i> No suspicious misinformation risk factors detected`;
            resRiskList.appendChild(li);
        }

        resExplanation.innerText = data.explanation;
    }

    async function loadAnalytics() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();

            document.getElementById('stat-total').innerText = data.total_samples || 50;
            document.getElementById('stat-fake').innerText = `${data.fake_count} (${data.fake_percentage}%)`;
            document.getElementById('stat-real').innerText = `${data.real_count} (${data.real_percentage}%)`;

            const catChart = document.getElementById('category-chart');
            catChart.innerHTML = '';
            if (data.categories) {
                const total = data.total_samples;
                Object.entries(data.categories).sort((a,b) => b[1] - a[1]).forEach(([cat, count]) => {
                    const pct = Math.round((count / total) * 100);
                    catChart.innerHTML += `
                        <div class="chart-bar-item">
                            <div class="bar-meta">
                                <span>${cat}</span>
                                <span style="font-family: 'JetBrains Mono', monospace;">${count} items (${pct}%)</span>
                            </div>
                            <div class="bar-track">
                                <div class="bar-fill" style="width: ${pct}%"></div>
                            </div>
                        </div>
                    `;
                });
            }

            const srcChart = document.getElementById('source-chart');
            srcChart.innerHTML = '';
            if (data.sources) {
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

            document.getElementById('metric-acc').innerText = `${(data.accuracy * 100).toFixed(1)}%`;
            document.getElementById('metric-prec').innerText = `${(data.precision * 100).toFixed(1)}%`;
            document.getElementById('metric-rec').innerText = `${(data.recall * 100).toFixed(1)}%`;
            document.getElementById('metric-f1').innerText = `${(data.f1_score * 100).toFixed(1)}%`;
        } catch (err) {
            console.error('Metrics load error:', err);
        }
    }
});
