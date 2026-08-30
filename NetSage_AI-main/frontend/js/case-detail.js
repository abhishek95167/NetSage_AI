/**
 * NetSage AI — Case Detail Page
 * Bento-Glass Diagnostic Inspector with Interactive Fault-Isolated Topology Visualizer
 */

let currentCase = null;
let currentDiagnosis = null;
let currentRuleCheck = null;

async function renderCaseDetail(caseId) {
    const container = document.getElementById('case-detail-content');
    container.innerHTML = `
        <div class="spinner-container">
            <div class="spinner"></div>
            <p class="loading-text">Extracting telemetry for ${escapeHtml(caseId)}...</p>
        </div>`;

    try {
        currentCase = await api.getCase(caseId);
        currentDiagnosis = await api.getDiagnosis(caseId);
        currentRuleCheck = await api.getRuleCheck(caseId);
        const reviews = await api.getReviews(caseId);

        container.innerHTML = buildCaseDetailHtml(currentCase, currentDiagnosis, currentRuleCheck, reviews);
        initGlassSpotlight();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Failed to load incident</h3><p>${err.message}</p></div>`;
    }
}

function buildCaseDetailHtml(caseData, diagnosis, ruleCheck, reviews) {
    const hasReviews = reviews && reviews.length > 0;
    const latestReview = hasReviews ? reviews[0] : null;

    let html = `
        <!-- Top Action Bar -->
        <div class="flex gap-3 mb-6 items-center" style="flex-wrap:wrap;">
            <button class="btn btn-primary btn-glow" onclick="runAIDiagnosis('${caseData.case_id}')" id="btnDiagnose">
                <span>Run Neural Diagnosis</span>
            </button>
            <button class="btn btn-secondary" onclick="runRuleCheck('${caseData.case_id}')" id="btnRuleCheck">
                <span>Run Rule Checker</span>
            </button>
            <button class="btn btn-ghost" onclick="navigateTo('cases')">
                <span>Back to Incident List</span>
            </button>
            <div style="margin-left:auto;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                ${statusBadge(caseData.status)}
                ${severityBadge(caseData.severity)}
                ${conceptBadge(caseData.concept)}
                ${osiLayerBadge(caseData.osi_layer)}
            </div>
        </div>

        <!-- Interactive Fault-Isolated Topology Visualizer -->
        <div class="mb-6 animate-stagger-1">
            ${renderTopologyLabVisualizer(caseData.concept || caseData.osi_layer, 'caseDetailTopologyLab')}
        </div>

        <!-- Incident Telemetry Bento Card -->
        <div class="bento-card glass-interactive mb-6 animate-stagger-1">
            <div class="bento-card-header">
                <div class="bento-title">Incident Telemetry & Packet Data — ${escapeHtml(caseData.case_id)}: ${escapeHtml(caseData.title)}</div>
                <span class="text-xs text-muted font-mono">${formatDateTime(caseData.created_at)}</span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px;">
                <div style="padding:14px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                    <div class="text-xs text-muted font-bold">REPORTED SYMPTOM</div>
                    <div class="text-sm" style="color:#ffffff;margin-top:4px;">${escapeHtml(caseData.symptom)}</div>
                </div>
                <div style="padding:14px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                    <div class="text-xs text-muted font-bold">GROUND TRUTH FAULT LABEL</div>
                    <div class="text-sm font-mono" style="color:var(--brand-primary);margin-top:4px;">${escapeHtml(caseData.expected_fault) || 'Not specified'}</div>
                </div>
            </div>
            ${caseData.topology_notes ? `
                <div style="margin-bottom:18px;padding:14px;background:rgba(0,0,0,0.25);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                    <div class="text-xs text-muted font-bold">TOPOLOGY NOTES</div>
                    <div class="text-sm text-secondary" style="margin-top:4px;">${escapeHtml(caseData.topology_notes)}</div>
                </div>
            ` : ''}
            <div>
                <div class="text-xs text-muted font-bold mb-2">RAW CISCO IOS SHOW OUTPUTS</div>
                ${caseData.show_outputs ? terminalBlock(caseData.show_outputs, 'Cisco IOS Telemetry Feed') : '<span class="text-muted">No show output commands provided</span>'}
            </div>
        </div>
    `;

    // AI Diagnosis Section
    html += `<div id="diagnosis-section" class="animate-stagger-2">`;
    if (diagnosis) {
        html += buildDiagnosisCard(diagnosis);
    } else {
        html += `
            <div class="bento-card glass-interactive mb-6">
                <div class="empty-state" style="padding:32px;">
                    <h3>No AI Diagnosis Generated</h3>
                    <p>Click "Run Neural Diagnosis" to initiate dual-engine neural telemetry scanning</p>
                </div>
            </div>`;
    }
    html += `</div>`;

    // Rule Checker Section
    html += `<div id="rule-check-section" class="animate-stagger-3">`;
    if (ruleCheck && ruleCheck.results) {
        html += buildRuleCheckCard(ruleCheck);
    } else {
        html += `
            <div class="bento-card glass-interactive mb-6">
                <div class="empty-state" style="padding:32px;">
                    <h3>Deterministic Rules Not Executed</h3>
                    <p>Click "Run Rule Checker" to scan show outputs against deterministic heuristics</p>
                </div>
            </div>`;
    }
    html += `</div>`;

    // Human Review Section
    html += `<div id="review-section" class="animate-stagger-4">`;
    if (diagnosis && !latestReview) {
        html += buildReviewPanel(caseData.case_id);
    } else if (latestReview) {
        html += buildReviewResult(latestReview, reviews);
    }
    html += `</div>`;

    return html;
}

function buildDiagnosisCard(diag) {
    const conf = confidenceLabel(diag.confidence);
    const evidenceItems = (diag.evidence || []).map(e => `<li>${escapeHtml(e)}</li>`).join('');
    const fixItems = (diag.fix_steps || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');
    const altItems = (diag.alternative_causes || []).map(a => `<li>${escapeHtml(a)}</li>`).join('');

    return `
        <div class="bento-card glass-interactive mb-6" style="border-color:var(--brand-primary);">
            <div class="bento-card-header" style="border-bottom:1px solid var(--glass-border);padding-bottom:16px;">
                <div class="bento-title">
                    <span>Neural Root Cause Telemetry</span>
                    ${diag.is_demo_mode ? '<span class="badge badge-analyzed">DEMO INFERENCE</span>' : '<span class="badge badge-resolved">LIVE NEURAL</span>'}
                </div>
                <div>${osiLayerBadge(diag.osi_layer)}</div>
            </div>

            <div style="margin-bottom:20px;">
                <div class="text-xs text-muted font-bold">DIAGNOSED ROOT CAUSE</div>
                <div style="font-size:1.15rem;font-weight:800;color:#ffffff;margin-top:6px;line-height:1.5;">${escapeHtml(diag.root_cause)}</div>
            </div>

            <div style="margin-bottom:22px;">
                <div class="flex justify-between items-center mb-2">
                    <span class="text-xs text-muted font-bold">INFERENCE CONFIDENCE</span>
                    <span style="font-weight:800;color:${diag.confidence >= 85 ? 'var(--brand-primary)' : diag.confidence >= 60 ? 'var(--brand-accent)' : '#ff3366'}">${diag.confidence}% (${conf.text})</span>
                </div>
                <div style="height:10px;background:rgba(255,255,255,0.08);border-radius:var(--radius-pill);overflow:hidden;">
                    <div style="height:100%;width:${diag.confidence}%;border-radius:var(--radius-pill);background:linear-gradient(90deg, #00e676, var(--neon-emerald));box-shadow:0 0 12px var(--neon-emerald);"></div>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
                <div style="padding:16px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                    <div class="text-xs text-muted font-bold mb-2">TELEMETRY EVIDENCE CITED</div>
                    <ul class="evidence-list" style="padding:0;list-style:none;">${evidenceItems || '<li class="text-muted">No specific evidence listed</li>'}</ul>
                </div>
                <div style="padding:16px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                    <div class="text-xs text-muted font-bold mb-2">RECOMMENDED VERIFICATION CLI</div>
                    <div class="font-mono text-sm" style="color:var(--brand-primary);padding:10px;background:rgba(0,0,0,0.4);border-radius:var(--radius-sm);">${escapeHtml(diag.next_command) || 'N/A'}</div>
                </div>
            </div>

            <div style="padding:18px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);">
                <div class="text-xs text-muted font-bold mb-2">ACTIONABLE REMEDIATION PROCEDURE</div>
                <ol class="fix-steps" style="padding:0;list-style:none;">${fixItems || '<li class="text-muted">No fix steps provided</li>'}</ol>
            </div>

            ${altItems ? `
                <div style="margin-top:16px;padding:14px;background:rgba(255,255,255,0.02);border-radius:var(--radius-md);">
                    <div class="text-xs text-muted font-bold mb-2">ALTERNATIVE ROOT CAUSES CONSIDERED</div>
                    <ul class="evidence-list">${altItems}</ul>
                </div>
            ` : ''}
        </div>
    `;
}

function buildRuleCheckCard(ruleCheck) {
    const results = ruleCheck.results || [];
    const failures = results.filter(r => r.status === 'FAIL');
    const passes = results.filter(r => r.status === 'PASS');

    const resultItems = results.map(r => {
        const isFail = r.status === 'FAIL';
        return `
            <div class="rule-result ${isFail ? 'fail' : 'pass'}" style="display:flex;gap:14px;padding:14px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--glass-border);margin-bottom:10px;border-left:4px solid ${isFail ? 'var(--severity-high)' : 'var(--severity-low)'};">
                <div style="font-size:0.8rem;font-weight:800;padding:4px 8px;border-radius:4px;background:${isFail ? 'rgba(255,51,102,0.2)' : 'rgba(0,230,118,0.2)'};color:${isFail ? '#ff6b8b' : '#33eb91'};align-self:flex-start;">${isFail ? 'FAIL' : 'PASS'}</div>
                <div style="flex:1;">
                    <div style="font-weight:700;font-size:0.92rem;color:#ffffff;display:flex;align-items:center;gap:8px;">
                        <span>${escapeHtml(r.check.replace(/_/g, ' ').toUpperCase())}</span>
                        ${severityBadge(r.severity)}
                    </div>
                    <div style="font-size:0.86rem;color:var(--text-secondary);margin-top:3px;">${escapeHtml(r.message)}</div>
                    ${r.evidence && isFail ? `<div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:var(--text-muted);margin-top:6px;background:rgba(0,0,0,0.4);padding:6px 10px;border-radius:4px;">${escapeHtml(r.evidence)}</div>` : ''}
                </div>
            </div>`;
    }).join('');

    return `
        <div class="bento-card glass-interactive mb-6">
            <div class="bento-card-header">
                <div class="bento-title">Deterministic Rule Engine</div>
                <span class="text-xs text-muted font-mono">${failures.length} anomalies detected, ${passes.length} verified rules</span>
            </div>
            <div>${resultItems}</div>
        </div>`;
}

function buildReviewPanel(caseId) {
    return `
        <div class="bento-card glass-interactive mb-6" style="border-color:var(--brand-accent);">
            <div class="bento-card-header" style="border-bottom:1px solid rgba(255,184,0,0.3);padding-bottom:14px;">
                <div class="bento-title" style="color:var(--brand-accent);">
                    <span>Human-in-the-Loop Sign-Off</span>
                </div>
                <span class="badge badge-high">Governance Required</span>
            </div>
            <div style="padding-top:14px;">
                <p class="text-secondary text-sm mb-4">Under NetSage AI Responsible AI Governance, all AI diagnostic outputs must be inspected by a certified network engineer before applying corrective configuration changes to hardware.</p>

                <div class="form-group">
                    <label class="form-label">Engineer Notes & Verification</label>
                    <textarea class="form-textarea" id="reviewNotes" rows="3" placeholder="Provide notes justifying your validation decision..."></textarea>
                </div>

                <div class="form-group hidden" id="editDiagnosisGroup">
                    <label class="form-label">Corrected Engineer Diagnosis</label>
                    <textarea class="form-textarea" id="editedDiagnosis" rows="3" placeholder="Specify your corrected root-cause analysis..."></textarea>
                </div>

                <div class="flex gap-3 mt-4" style="flex-wrap:wrap;">
                    <button class="btn btn-success btn-lg" onclick="submitReview('${caseId}', 'accepted')">
                        <span>Accept Analysis</span>
                    </button>
                    <button class="btn btn-warning btn-lg" onclick="showEditField(); return false;">
                        <span>Edit & Correct</span>
                    </button>
                    <button class="btn btn-danger btn-lg" onclick="submitReview('${caseId}', 'rejected')">
                        <span>Reject Analysis</span>
                    </button>
                </div>
            </div>
        </div>`;
}

function showEditField() {
    document.getElementById('editDiagnosisGroup').classList.remove('hidden');
    const editBtn = document.querySelector('.btn-warning');
    if (editBtn) {
        editBtn.innerHTML = '<span>Submit Corrected Diagnosis</span>';
        editBtn.onclick = () => submitReview(currentCase.case_id, 'edited');
    }
}

function buildReviewResult(latestReview, allReviews) {
    const decisionColors = { accepted: 'var(--decision-accepted)', edited: 'var(--decision-edited)', rejected: 'var(--decision-rejected)' };

    let historyHtml = (allReviews || []).map(r => `
        <div class="flex gap-3 items-center" style="padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
            <div style="flex:1;">
                <div style="font-weight:800;color:${decisionColors[r.decision] || 'white'};">${r.decision.toUpperCase()}</div>
                ${r.reviewer_notes ? `<div class="text-sm text-secondary" style="margin-top:2px;">${escapeHtml(r.reviewer_notes)}</div>` : ''}
                ${r.edited_diagnosis ? `<div class="text-sm" style="color:var(--brand-accent);margin-top:4px;"><strong>Correction:</strong> ${escapeHtml(r.edited_diagnosis)}</div>` : ''}
            </div>
            <span class="text-xs text-muted font-mono">${formatDateTime(r.created_at)}</span>
        </div>
    `).join('');

    return `
        <div class="bento-card glass-interactive mb-6">
            <div class="bento-card-header">
                <div class="bento-title">Human Governance Record</div>
                ${decisionBadge(latestReview.decision)}
            </div>
            <div>
                ${historyHtml}
                <button class="btn btn-ghost btn-sm mt-4" onclick="reReview('${currentCase.case_id}')">Submit New Sign-Off Review</button>
            </div>
        </div>`;
}

function reReview(caseId) {
    const reviewSection = document.getElementById('review-section');
    reviewSection.innerHTML = buildReviewPanel(caseId);
    initGlassSpotlight();
}

async function runAIDiagnosis(caseId) {
    const btn = document.getElementById('btnDiagnose');
    btn.innerHTML = '<span>Scanning Telemetry...</span>';
    btn.disabled = true;

    try {
        currentDiagnosis = await api.runDiagnosis(caseId);
        showToast('Neural diagnosis generated successfully', 'success');

        const diagSection = document.getElementById('diagnosis-section');
        diagSection.innerHTML = buildDiagnosisCard(currentDiagnosis);

        const reviewSection = document.getElementById('review-section');
        reviewSection.innerHTML = buildReviewPanel(caseId);
        initGlassSpotlight();
    } catch (err) {
        showToast(`Diagnosis error: ${err.message}`, 'error');
    } finally {
        btn.innerHTML = '<span>Run Neural Diagnosis</span>';
        btn.disabled = false;
    }
}

async function runRuleCheck(caseId) {
    const btn = document.getElementById('btnRuleCheck');
    btn.innerHTML = '<span>Checking Heuristics...</span>';
    btn.disabled = true;

    try {
        currentRuleCheck = await api.runRuleCheck(caseId);
        showToast('Rule heuristics analysis complete', 'success');

        const ruleSection = document.getElementById('rule-check-section');
        ruleSection.innerHTML = buildRuleCheckCard(currentRuleCheck);
        initGlassSpotlight();
    } catch (err) {
        showToast(`Rule check failed: ${err.message}`, 'error');
    } finally {
        btn.innerHTML = '<span>Run Rule Checker</span>';
        btn.disabled = false;
    }
}

async function submitReview(caseId, decision) {
    const notes = document.getElementById('reviewNotes')?.value || '';
    const edited = document.getElementById('editedDiagnosis')?.value || '';

    try {
        await api.submitReview(caseId, {
            decision: decision,
            edited_diagnosis: edited,
            reviewer_notes: notes
        });

        showToast(`Governance review recorded: ${decision.toUpperCase()}`, 'success');
        await renderCaseDetail(caseId);
    } catch (err) {
        showToast(`Review recording failed: ${err.message}`, 'error');
    }
}
