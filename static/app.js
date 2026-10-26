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
                loadRobustnessBenchmark();
            } else if (target === 'tab-artifacts') {
                loadMetrics();
            }
        });
    });

    // Predictor Elements
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

    const baseBanner = document.getElementById('base-banner');
    const baseIcon = document.getElementById('base-icon');
    const baseTitle = document.getElementById('base-title');
    const baseSubtitle = document.getElementById('base-subtitle');
    const baseProbs = document.getElementById('base-probs');

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
    async function runDualAnalysis(text, isRetry = false) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Evaluating Models & Explainability...';

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!res.ok) {
                const errDetail = await res.text();
                throw new Error(errDetail || 'API request failed');
            }

            const data = await res.json();
            renderDualResults(data);
        } catch (err) {
            console.warn('Analysis request error:', err);
            if (!isRetry) {
                // Auto-retry once in case server was reloading or warming up models
                btnAnalyze.innerHTML = '<i class="fa-solid fa-arrows-rotate fa-spin"></i> Connecting to models...';
                await new Promise(r => setTimeout(r, 1500));
                return runDualAnalysis(text, true);
            }
            alert('Could not connect to backend server. If you just started or reloaded the server, neural models take ~10 seconds to load into memory. Please press Ctrl+F5 to hard-refresh the page and try again.');
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = '<i class="fa-solid fa-code-compare"></i> Compare MuRIL vs IndicBERT';
        }
    }

    // Render Dual Model & Misinformation Intelligence Results
    function renderDualResults(data) {
        if (resultEmpty) resultEmpty.classList.add('hidden');
        if (resultDetails) {
            resultDetails.classList.remove('hidden');
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
        const isFakeM = m.label === 1 || m.label_name === "Fake";
        if (murilBanner) murilBanner.className = `verdict-banner ${isFakeM ? 'fake' : 'real'}`;
        if (murilIcon) murilIcon.innerHTML = isFakeM ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        if (murilTitle) murilTitle.innerText = m.label_name;
        if (murilSubtitle) murilSubtitle.innerText = `Confidence: ${m.confidence}%`;
        if (murilProbs) murilProbs.innerText = `Real: ${(m.probabilities.Real * 100).toFixed(1)}% | Fake: ${(m.probabilities.Fake * 100).toFixed(1)}%`;

        // IndicBERT Card
        const ind = data.indicbert_results;
        const isFakeI = ind.label === 1 || ind.label_name === "Fake";
        if (indicBanner) indicBanner.className = `verdict-banner ${isFakeI ? 'fake' : 'real'}`;
        if (indicIcon) indicIcon.innerHTML = isFakeI ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
        if (indicTitle) indicTitle.innerText = ind.label_name;
        if (indicSubtitle) indicSubtitle.innerText = `Confidence: ${ind.confidence}%`;
        if (indicProbs) indicProbs.innerText = `Real: ${(ind.probabilities.Real * 100).toFixed(1)}% | Fake: ${(ind.probabilities.Fake * 100).toFixed(1)}%`;

        // Base Model Card (TF-IDF Baseline)
        if (data.base_model_results) {
            const b = data.base_model_results;
            const isFakeB = b.label_name === 'Fake' || b.predicted_label === 'Fake' || b.label === 1;
            if (baseBanner) baseBanner.className = `verdict-banner ${isFakeB ? 'fake' : 'real'}`;
            if (baseIcon) baseIcon.innerHTML = isFakeB ? '<i class="fa-solid fa-triangle-exclamation"></i>' : '<i class="fa-solid fa-circle-check"></i>';
            if (baseTitle) baseTitle.innerText = b.label_name || b.predicted_label;
            if (baseSubtitle) baseSubtitle.innerText = `Confidence: ${b.confidence}%`;
            if (baseProbs && b.probabilities) baseProbs.innerText = `Real: ${(b.probabilities.Real * 100).toFixed(1)}% | Fake: ${(b.probabilities.Fake * 100).toFixed(1)}%`;
        }

        // Deployment Decision Updates
        if (data.model_selection_decision) {
            const dec = data.model_selection_decision;
            const selModel = document.getElementById('selection-model-name');
            const selSum = document.getElementById('selection-verdict-summary');
            const selMuril = document.getElementById('sel-stat-muril');
            const selIndic = document.getElementById('sel-stat-indic');
            const selBase = document.getElementById('sel-stat-base');
            if (selModel) selModel.innerHTML = `<i class="fa-solid fa-crown" style="color: #F59E0B;"></i> ${dec.selected_model}`;
            if (selSum) selSum.innerHTML = dec.decision_summary;
            if (selMuril && dec.accuracy_comparison) selMuril.innerText = `${dec.accuracy_comparison.muril_accuracy}%`;
            if (selIndic && dec.accuracy_comparison) selIndic.innerText = `${dec.accuracy_comparison.indicbert_accuracy}%`;
            if (selBase && dec.accuracy_comparison) selBase.innerText = `${dec.accuracy_comparison.base_model_accuracy}%`;
        }

        // Real-Time Ground Truth Fact-Check Card
        if (data.realtime_verification) {
            const rt = data.realtime_verification;
            const rtEngineTag = document.getElementById('rt-engine-tag');
            const rtBadge = document.getElementById('rt-verdict-badge');
            const rtChecker = document.getElementById('rt-checker-val');
            const rtRating = document.getElementById('rt-rating-val');
            const rtLatency = document.getElementById('rt-latency-val');
            const rtEvidence = document.getElementById('rt-evidence-text');
            const rtSourceLink = document.getElementById('rt-source-link');

            if (rtEngineTag) {
                rtEngineTag.innerHTML = `<i class="fa-solid fa-satellite-dish"></i> ${rt.provider || 'Live Grounding Engine'}`;
            }

            if (rtBadge) {
                const verdict = (rt.verdict || '').toUpperCase();
                if (verdict.includes('DEBUNKED') || verdict.includes('FAKE') || verdict.includes('HOAX')) {
                    rtBadge.className = 'realtime-status-pill debunked';
                    rtBadge.innerHTML = 'LIVE FACT CHECK: DEBUNKED HOAX ✖';
                } else if (verdict.includes('AUTHENTIC') || verdict.includes('REAL') || verdict.includes('VERIFIED')) {
                    rtBadge.className = 'realtime-status-pill authentic';
                    rtBadge.innerHTML = 'LIVE FACT CHECK: VERIFIED AUTHENTIC ✔';
                } else {
                    rtBadge.className = 'realtime-status-pill unverified';
                    rtBadge.innerHTML = 'LIVE FACT CHECK: UNCONFIRMED / NEUTRAL ℹ';
                }
            }

            if (rtChecker) rtChecker.innerText = rt.fact_checker || 'BoomLive / PIB Fact Check / Wikipedia';
            if (rtRating) {
                rtRating.innerText = rt.rating || 'Verified Claim';
                const vUpper = (rt.verdict || '').toUpperCase();
                rtRating.style.color = (vUpper.includes('DEBUNKED') || vUpper.includes('FAKE')) ? 'var(--verdict-fake)' : (vUpper.includes('AUTHENTIC') ? 'var(--verdict-real)' : 'var(--amber-gold)');
            }
            if (rtLatency) rtLatency.innerText = `${rt.latency_ms || 0} ms (${rt.latency_ms < 50 ? 'Ultra-Fast' : 'Live'})`;
            if (rtEvidence) rtEvidence.innerText = rt.summary || 'Corroborated against real-time ground truth sources.';

            if (rtSourceLink) {
                if (rt.url && rt.url.startsWith('http')) {
                    rtSourceLink.href = rt.url;
                    rtSourceLink.innerText = 'View Official Verification Record';
                    rtSourceLink.style.display = 'inline-flex';
                } else {
                    rtSourceLink.style.display = 'none';
                }
            }

            if (data.realtime_dataset_ingested && typeof updateDatasetStats === 'function') {
                updateDatasetStats();
            }
        }

        // Linguistic Analysis
        if (resLangType) resLangType.innerText = data.code_mix_type;
        if (resCmi) resCmi.innerText = `${data.cmi}%`;
        if (resCategory) resCategory.innerText = data.category;
        if (resRatio) resRatio.innerText = `${data.tanglish_pct}% / ${data.english_pct}%`;

        // AI Summary
        const aiSummaryEl = document.getElementById('res-ai-summary');
        if (aiSummaryEl) {
            aiSummaryEl.innerHTML = data.ai_summary;
        }

        // Decision Reliability Banner
        const rel = data.agreement_analysis;
        const relBadge = document.getElementById('res-rel-badge');
        const relHeadline = document.getElementById('res-rel-headline');
        const relDiagnosis = document.getElementById('res-rel-diagnosis');
        if (relBadge) {
            relBadge.className = `reliability-badge ${rel.reliability_color}`;
            relBadge.innerText = `${rel.decision_reliability} RELIABILITY`;
        }
        if (relHeadline) relHeadline.innerText = rel.headline;
        if (relDiagnosis) relDiagnosis.innerText = rel.diagnosis;

        // Misinformation Risk Score
        const risk = data.risk_score_analysis;
        const riskScoreVal = document.getElementById('res-risk-score-val');
        const riskScoreTier = document.getElementById('res-risk-score-tier');
        const riskSummary = document.getElementById('res-risk-summary');

        if (riskScoreVal) {
            riskScoreVal.className = `risk-dial-val ${risk.risk_color}`;
            riskScoreVal.innerText = risk.final_risk_score;
        }
        if (riskScoreTier) {
            riskScoreTier.style.color = `var(--verdict-${risk.risk_color === 'rose' || risk.risk_color === 'orange' ? 'fake' : 'real'})`;
            riskScoreTier.innerText = risk.risk_level;
        }
        if (riskSummary) riskSummary.innerText = risk.risk_summary;

        // Breakdown bars
        const b = risk.breakdown;
        setProgressBar('bar-risk-model', 'val-risk-model', b.model_evidence);
        setProgressBar('bar-risk-agree', 'val-risk-agree', b.model_agreement);
        setProgressBar('bar-risk-signals', 'val-risk-signals', b.risk_signals);
        setProgressBar('bar-risk-robust', 'val-risk-robust', b.robustness);

        // Claim Extraction Card
        const claim = data.claim_analysis;
        const claimQuote = document.getElementById('res-claim-quote');
        const claimDomain = document.getElementById('res-claim-domain');
        const claimCausal = document.getElementById('res-claim-causal');
        const claimCitation = document.getElementById('res-claim-citation');

        if (claimQuote) claimQuote.innerText = `"${claim.formal_claim_statement}"`;
        if (claimDomain) claimDomain.innerHTML = `<i class="fa-solid fa-shapes"></i> ${claim.claim_type}`;
        if (claimCausal) {
            claimCausal.innerHTML = claim.is_causal_claim
                ? '<i class="fa-solid fa-link text-rose"></i> Causal Assertion Flagged'
                : '<i class="fa-solid fa-check text-emerald"></i> Descriptive / Non-Causal';
        }
        if (claimCitation) {
            claimCitation.innerHTML = claim.has_verifiable_citation
                ? '<i class="fa-solid fa-building-columns text-emerald"></i> Official Citation Reference'
                : '<i class="fa-solid fa-circle-exclamation text-amber"></i> No Cited Institutional Source';
        }

        // Explainability Signals
        const signalsGrid = document.getElementById('res-signals-grid');
        if (signalsGrid && data.explainability) {
            signalsGrid.innerHTML = '';
            const sigs = data.explainability.signals;
            if (sigs && sigs.length > 0) {
                sigs.forEach(s => {
                    signalsGrid.innerHTML += `
                        <div class="signal-tile">
                            <div class="signal-tile-header">
                                <span class="signal-name">${s.name}</span>
                                <span class="signal-badge ${s.severity}">${s.severity}</span>
                            </div>
                            <p class="signal-desc">${s.explanation}</p>
                            <span class="signal-evidence">Token: "${s.evidence.join('", "')}"</span>
                        </div>
                    `;
                });
            } else {
                signalsGrid.innerHTML = `
                    <div class="signal-tile" style="grid-column: 1 / -1; background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.25);">
                        <div class="signal-tile-header">
                            <span class="signal-name" style="color: #34D399;"><i class="fa-solid fa-circle-check"></i> Neutral Linguistic Phrasing</span>
                            <span class="signal-badge" style="background: rgba(16, 185, 129, 0.2); color: #34D399;">CLEAN</span>
                        </div>
                        <p class="signal-desc">No sensationalist clickbait, artificial urgency, or pseudo-scientific health/conspiracy indicators detected.</p>
                    </div>
                `;
            }
        }

        // Quick button to send text into Robustness Lab
        const btnSendToRob = document.getElementById('btn-send-to-robustness');
        if (btnSendToRob) {
            btnSendToRob.onclick = () => {
                const robTab = document.querySelector('[data-tab="tab-robustness"]');
                if (robTab) robTab.click();
                const robInput = document.getElementById('robustness-input');
                if (robInput) {
                    robInput.value = data.text;
                    runRobustnessLab(data.text);
                }
            };
        }
    }

    function setProgressBar(barId, valId, score) {
        const bar = document.getElementById(barId);
        const val = document.getElementById(valId);
        if (bar) bar.style.width = `${Math.min(100, Math.max(0, score))}%`;
        if (val) val.innerText = `${score}/100`;
    }

    // =========================================================================
    // TANGLISH ROBUSTNESS LAB CONTROLS
    // =========================================================================
    const robInput = document.getElementById('robustness-input');
    const btnRunRob = document.getElementById('btn-run-robustness');
    const robPresets = document.querySelectorAll('.rob-preset-btn');
    const robResults = document.getElementById('robustness-results');

    robPresets.forEach(btn => {
        btn.addEventListener('click', () => {
            if (!btn.dataset.preset) return;
            if (robInput) robInput.value = btn.dataset.preset;
            runRobustnessLab(btn.dataset.preset);
        });
    });

    if (btnRunRob) {
        btnRunRob.addEventListener('click', () => {
            const text = robInput ? robInput.value.trim() : '';
            if (text) {
                runRobustnessLab(text);
            } else if (robInput) {
                robInput.focus();
            }
        });
    }

    async function runRobustnessLab(text) {
        if (!btnRunRob) return;
        btnRunRob.disabled = true;
        btnRunRob.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating Variations & Testing Encoders...';

        try {
            const res = await fetch('/api/robustness', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            if (!res.ok) throw new Error('Robustness API failed');

            const data = await res.json();
            renderRobustnessLabResults(data);
        } catch (err) {
            console.error('Robustness Lab Error:', err);
            alert('Failed to execute robustness perturbation test. Please ensure backend is running.');
        } finally {
            btnRunRob.disabled = false;
            btnRunRob.innerHTML = '<i class="fa-solid fa-flask-vial"></i> Run Perturbation Experiment';
        }
    }

    function renderRobustnessLabResults(data) {
        if (robResults) {
            robResults.classList.remove('hidden');
            robResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // Summary Metric Tiles
        const scoreEl = document.getElementById('rob-score-val');
        const murilStabEl = document.getElementById('rob-muril-stab');
        const indicStabEl = document.getElementById('rob-indic-stab');
        const agrRateEl = document.getElementById('rob-agree-rate');

        if (scoreEl) scoreEl.innerText = `${data.robustness_score}%`;
        if (murilStabEl) murilStabEl.innerText = `${data.muril_stability_pct}%`;
        if (indicStabEl) indicStabEl.innerText = `${data.indic_stability_pct}%`;
        if (agrRateEl) agrRateEl.innerText = `${data.agreement_rate_pct}%`;

        // Research Observation Box
        const resObsEl = document.getElementById('rob-research-obs');
        if (resObsEl) resObsEl.innerText = data.research_observation;

        // Populate Variants Table
        const tableBody = document.getElementById('rob-table-body');
        if (tableBody && data.variants_table) {
            tableBody.innerHTML = '';
            data.variants_table.forEach(r => {
                const isOrig = r.variant_id === 0;
                const tr = document.createElement('tr');
                if (isOrig) tr.style.background = 'rgba(99, 102, 241, 0.08)';

                const mShiftStr = r.muril_shift !== 0 ? ` (${r.muril_shift > 0 ? '+' : ''}${r.muril_shift}%)` : '';
                const iShiftStr = r.indic_shift !== 0 ? ` (${r.indic_shift > 0 ? '+' : ''}${r.indic_shift}%)` : '';

                tr.innerHTML = `
                    <td>
                        <strong style="color: ${isOrig ? 'var(--primary-indigo)' : 'var(--text-pure)'};">
                            ${isOrig ? '<i class="fa-solid fa-star"></i> Baseline' : `Var #${r.variant_id}`}
                        </strong>
                        <div style="font-size: 11px; color: var(--text-muted);">${r.type}</div>
                    </td>
                    <td style="max-width: 320px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary);">
                        ${r.text}
                    </td>
                    <td>
                        <span class="table-pill ${r.muril_label === 'Fake' ? 'fake' : 'real'}">
                            ${r.muril_label} ${r.muril_conf}%
                        </span>
                        <div style="font-size: 10.5px; color: ${r.muril_shift < 0 ? '#FB7185' : '#34D399'}; font-family: monospace;">
                            ${mShiftStr}
                        </div>
                    </td>
                    <td>
                        <span class="table-pill ${r.indic_label === 'Fake' ? 'fake' : 'real'}">
                            ${r.indic_label} ${r.indic_conf}%
                        </span>
                        <div style="font-size: 10.5px; color: ${r.indic_shift < 0 ? '#FB7185' : '#34D399'}; font-family: monospace;">
                            ${iShiftStr}
                        </div>
                    </td>
                    <td style="text-align: center;">
                        ${r.agreement ? '<i class="fa-solid fa-circle-check" style="color: #10B981; font-size: 15px;"></i>' : '<i class="fa-solid fa-triangle-exclamation" style="color: #F43F5E; font-size: 15px;"></i>'}
                    </td>
                    <td>
                        <span class="table-pill ${r.overall_stable ? 'stable' : 'flipped'}">
                            ${r.overall_stable ? '✓ Stable' : '⚠ Flipped'}
                        </span>
                    </td>
                `;
                tableBody.appendChild(tr);
            });
        }
    }

    // =========================================================================
    // BENCHMARK ANALYTICS & RESEARCH EXPERIMENTS
    // =========================================================================
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

    async function loadRobustnessBenchmark() {
        try {
            const res = await fetch('/api/robustness-benchmark');
            const data = await res.json();

            // 1. Standard vs Robustness Table
            const benchTableBody = document.getElementById('benchmark-metrics-body');
            if (benchTableBody && data.standard_vs_robustness) {
                benchTableBody.innerHTML = '';
                data.standard_vs_robustness.metrics.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="font-weight: 600; color: var(--text-pure);">${row.metric}</td>
                        <td style="font-family: 'JetBrains Mono', monospace; color: #94A3B8;">${row.base || '--'}</td>
                        <td style="font-family: 'JetBrains Mono', monospace; color: #2DD4BF;">${row.indicbert}</td>
                        <td style="font-family: 'JetBrains Mono', monospace; color: #818CF8; font-weight: 700;">${row.muril}</td>
                        <td><span class="badge-tag highlight" style="font-size: 11px;">${row.leader}</span></td>
                    `;
                    benchTableBody.appendChild(tr);
                });
            }

            // 2. 3-Way Experiment Cards
            const expGrid = document.getElementById('three-way-exp-grid');
            if (expGrid && data.three_way_linguistic_experiment) {
                expGrid.innerHTML = '';
                data.three_way_linguistic_experiment.groups.forEach(g => {
                    expGrid.innerHTML += `
                        <div class="exp-group-card">
                            <div class="exp-group-header">
                                <span class="exp-group-badge">Group ${g.group_id}</span>
                                <span class="badge-tag" style="font-size: 10px;">CMI: ${g.avg_cmi}%</span>
                            </div>
                            <div class="exp-group-title">${g.name}</div>
                            <div class="exp-metric-row">
                                <span class="exp-metric-label">Google MuRIL Acc</span>
                                <span class="exp-metric-val" style="color: #818CF8;">${g.muril_accuracy}</span>
                            </div>
                            <div class="exp-metric-row">
                                <span class="exp-metric-label">IndicBERT Acc</span>
                                <span class="exp-metric-val" style="color: #2DD4BF;">${g.indic_accuracy}</span>
                            </div>
                            <div class="exp-metric-row">
                                <span class="exp-metric-label">Agreement Rate</span>
                                <span class="exp-metric-val">${g.agreement_rate}</span>
                            </div>
                            <div class="exp-metric-row">
                                <span class="exp-metric-label">Stability Regime</span>
                                <span class="exp-metric-val" style="color: #F59E0B;">${g.stability_status}</span>
                            </div>
                            <p style="font-size: 11.5px; color: var(--text-muted); margin-top: 4px;">${g.notes}</p>
                        </div>
                    `;
                });

                const findingEl = document.getElementById('three-way-finding');
                if (findingEl) findingEl.innerText = data.three_way_linguistic_experiment.research_finding;
            }
        } catch (err) {
            console.error('Robustness benchmark load error:', err);
        }
    }

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
            if (data.base_model) {
                const el = document.getElementById('bm-base-acc');
                if (el) el.innerText = `${(data.base_model.accuracy * 100).toFixed(1)}%`;
            }
        } catch (err) {
            console.error('Metrics load error:', err);
        }
    }

    // =========================================================================
    // REAL-TIME API KEY MODAL & DATASET EXPANSION MANAGEMENT
    // =========================================================================
    const btnOpenApiModal = document.getElementById('btn-open-api-modal');
    const apiModal = document.getElementById('api-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalSave = document.getElementById('btn-modal-save');
    const apiKeyInput = document.getElementById('api-key-input');
    const modalKeyStatus = document.getElementById('modal-key-status');
    const headerApiStatus = document.getElementById('header-api-status');
    const corpusStatusLabel = document.getElementById('corpus-status-label');

    function openModal() {
        if (apiModal) {
            apiModal.style.display = 'flex';
            apiModal.classList.remove('hidden');
        }
    }

    function closeModal() {
        if (apiModal) {
            apiModal.style.display = 'none';
            apiModal.classList.add('hidden');
        }
    }

    if (btnOpenApiModal) btnOpenApiModal.addEventListener('click', openModal);
    if (btnCloseModal) btnCloseModal.addEventListener('click', closeModal);
    if (btnModalCancel) btnModalCancel.addEventListener('click', closeModal);
    if (apiModal) {
        apiModal.addEventListener('click', (e) => {
            if (e.target === apiModal) closeModal();
        });
    }

    async function loadApiConfig() {
        try {
            const res = await fetch('/api/config/api-key');
            if (!res.ok) return;
            const data = await res.json();
            if (data.has_key) {
                if (headerApiStatus) headerApiStatus.innerText = 'API: Google Cloud Active';
                if (modalKeyStatus) modalKeyStatus.innerText = `Key Active (${data.masked_key})`;
                if (apiKeyInput) apiKeyInput.placeholder = data.masked_key;
            } else {
                if (headerApiStatus) headerApiStatus.innerText = 'API: Free Live Engine';
                if (modalKeyStatus) modalKeyStatus.innerText = 'Current: Using Free Built-in Engine';
            }
        } catch (err) {
            console.error('Failed to load API config:', err);
        }
    }

    if (btnModalSave) {
        btnModalSave.addEventListener('click', async () => {
            const keyVal = apiKeyInput ? apiKeyInput.value.trim() : '';
            btnModalSave.disabled = true;
            btnModalSave.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
            try {
                const res = await fetch('/api/config/api-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ api_key: keyVal })
                });
                await res.json();
                closeModal();
                loadApiConfig();
            } catch (err) {
                console.error('Error saving API key:', err);
                alert('Could not save API key.');
            } finally {
                btnModalSave.disabled = false;
                btnModalSave.innerHTML = '<i class="fa-solid fa-check"></i> Save & Apply';
            }
        });
    }

    async function updateDatasetStats() {
        try {
            const res = await fetch('/api/stats');
            if (!res.ok) return;
            const data = await res.json();
            const liveCount = data.realtime_live_count || 0;
            const total = data.total_samples || (520 + liveCount);
            if (corpusStatusLabel) {
                corpusStatusLabel.innerText = `${total} Items (${data.base_corpus_count || 520} + ${liveCount} Live)`;
            }
            const dlDesc = document.getElementById('rt-dataset-download-desc');
            if (dlDesc) {
                dlDesc.innerText = `Real-Time Ingested Live Dataset (JSON) - contains ${liveCount} dynamically ingested live queries`;
            }
        } catch (err) {
            console.error('Failed to fetch dataset stats:', err);
        }
    }

    // Initialize API config and dataset counters on load
    loadApiConfig();
    updateDatasetStats();
});

