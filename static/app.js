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
    const resCmi = document.getElementById('res-cmi');
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
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

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
            alert('Error connecting to backend API.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<i class="fa-solid fa-microchip"></i> Analyze Credibility';
        }
    }

    function renderPredictionResult(data) {
        resultEmpty.classList.add('hidden');
        resultDetails.classList.remove('hidden');

        const isFake = data.label === 1;

        verdictBanner.className = `verdict-banner ${isFake ? 'fake' : 'real'}`;
        verdictIcon.innerHTML = isFake ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        verdictTitle.innerText = isFake ? 'FAKE NEWS' : 'VERIFIED REAL NEWS';
        verdictSubtitle.innerText = `Confidence Score: ${data.confidence}%`;

        gaugeFill.style.width = `${data.confidence}%`;
        gaugeScore.innerText = `${Math.round(data.confidence)}%`;

        resLangType.innerText = `${data.code_mix_type}`;
        resCmi.innerText = `${data.cmi}%`;
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

    const ragQueryInput = document.getElementById('rag-query-input');
    const btnRagSearch = document.getElementById('btn-rag-search');
    const ragResultsArea = document.getElementById('rag-results');

    btnRagSearch.addEventListener('click', () => {
        const query = ragQueryInput.value.trim();
        if (query) {
            runRagSearch(query);
        }
    });

    ragQueryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = ragQueryInput.value.trim();
            if (query) runRagSearch(query);
        }
    });

    async function runRagSearch(question) {
        btnRagSearch.disabled = true;
        btnRagSearch.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

        try {
            const res = await fetch('/api/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question, top_k: 3 })
            });

            const data = await res.json();
            renderRagResults(data);
        } catch (err) {
            console.error('RAG search error:', err);
            ragResultsArea.innerHTML = `<div class="empty-state">Error executing RAG search</div>`;
        } finally {
            btnRagSearch.disabled = false;
            btnRagSearch.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Search RAG';
        }
    }

    function renderRagResults(data) {
        let html = `
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.2); padding: 16px; border-radius: 12px; margin-bottom: 20px;">
                <span style="font-size: 11px; text-transform: uppercase; color: #A5B4FC; font-weight: 600;">Extracted Best Answer</span>
                <p style="font-size: 15px; margin-top: 4px; font-weight: 500;">"${data.answer}"</p>
                <span class="badge-tag" style="margin-top: 8px; display: inline-block;">Detected Lang: ${data.detected_language}</span>
            </div>
            <h3 style="font-size: 14px; margin-bottom: 12px;"><i class="fa-solid fa-layer-group"></i> Top Retrieved Documents (Hybrid Dense + BM25):</h3>
        `;

        if (data.retrieved_chunks && data.retrieved_chunks.length > 0) {
            data.retrieved_chunks.forEach((chunk, i) => {
                const score = data.relevance_scores ? (data.relevance_scores[i] * 100).toFixed(1) : 'N/A';
                const isFake = chunk.label === 1;
                html += `
                    <div class="rag-card-item">
                        <div class="rag-card-header">
                            <div>
                                <span class="badge-tag" style="background: ${isFake ? 'rgba(244,63,94,0.2)' : 'rgba(16,185,129,0.2)'}; color: ${isFake ? '#FDA4AF' : '#6EE7B7'}">
                                    ${chunk.label_name} (${chunk.category})
                                </span>
                                <span style="font-size: 12px; color: #94A3B8; margin-left: 8px;"><i class="fa-solid fa-share-nodes"></i> ${chunk.source}</span>
                            </div>
                            <span class="score-badge">Hybrid Score: ${score}%</span>
                        </div>
                        <p style="font-size: 14px; margin-top: 8px; color: #E2E8F0;">${chunk.text}</p>
                    </div>
                `;
            });
        }
        ragResultsArea.innerHTML = html;
    }

    async function loadAnalytics() {
        try {
            const res = await fetch('/api/stats');
            const data = await res.json();

            document.getElementById('stat-total').innerText = data.total_samples || 220;
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
