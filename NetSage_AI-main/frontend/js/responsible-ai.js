/**
 * NetSage AI — Responsible AI Page
 * Bento-Glass Governance Ledger & Transparency Logs
 */

async function renderResponsibleAI() {
    const container = document.getElementById('responsible-ai-content');
    try {
        const [logs, stats] = await Promise.all([
            api.getResponsibleAILog(),
            api.getDashboardStats()
        ]);
        container.innerHTML = buildResponsibleAIHtml(logs, stats);
        initGlassSpotlight();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Failed to load governance logs</h3><p>${err.message}</p></div>`;
    }
}

function buildResponsibleAIHtml(logs, stats) {
    const totalReviews = stats.accepted_diagnoses + stats.edited_diagnoses + stats.rejected_diagnoses;
    const agreementRate = totalReviews > 0 ? ((stats.accepted_diagnoses / totalReviews) * 100).toFixed(1) : 0;

    const statsHtml = `
        <div class="bento-grid animate-stagger-1">
            <div class="bento-col-3 bento-card glass-interactive" style="border-left:4px solid var(--decision-accepted);">
                <div class="text-xs text-muted font-bold">ACCEPTED INFERENCES</div>
                <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:var(--decision-accepted);">${stats.accepted_diagnoses}</div>
                <div class="text-xs text-secondary">Confirmed ground truth root causes</div>
            </div>
            <div class="bento-col-3 bento-card glass-interactive" style="border-left:4px solid var(--decision-edited);">
                <div class="text-xs text-muted font-bold">EDITED INFERENCES</div>
                <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:var(--decision-edited);">${stats.edited_diagnoses}</div>
                <div class="text-xs text-secondary">Engineer modified & refined</div>
            </div>
            <div class="bento-col-3 bento-card glass-interactive" style="border-left:4px solid var(--decision-rejected);">
                <div class="text-xs text-muted font-bold">REJECTED INFERENCES</div>
                <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:var(--decision-rejected);">${stats.rejected_diagnoses}</div>
                <div class="text-xs text-secondary">Model hallucinations flagged</div>
            </div>
            <div class="bento-col-3 bento-card glass-interactive" style="border-left:4px solid var(--brand-primary);">
                <div class="text-xs text-muted font-bold">AGREEMENT SCORE</div>
                <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:var(--brand-primary);">${agreementRate}%</div>
                <div class="text-xs text-secondary">Accepted / Total Reviewed × 100</div>
            </div>
        </div>
    `;

    const formula = `
        <div class="bento-card glass-interactive mb-6 animate-stagger-2">
            <div class="bento-card-header">
                <div class="bento-title">Mathematical Governance Formulation</div>
            </div>
            <div class="text-center" style="font-family:'JetBrains Mono',monospace;padding:24px;">
                <div style="color:var(--brand-primary);font-size:1.15rem;font-weight:700;margin-bottom:10px;text-shadow:0 0 15px rgba(0,242,174,0.3);">
                    AI-Human Agreement Precision Metric
                </div>
                <div style="color:var(--text-secondary);font-size:0.95rem;">
                    Agreement Rate = (Accepted Decisions / Total Completed Reviews) × 100
                </div>
                <div style="color:var(--text-primary);margin-top:14px;font-size:1.3rem;font-weight:700;">
                    = ${stats.accepted_diagnoses} / ${totalReviews} × 100 = 
                    <span style="color:var(--brand-accent);text-shadow:0 0 20px rgba(255,184,0,0.4);font-size:1.5rem;">${agreementRate}%</span>
                </div>
            </div>
        </div>
    `;

    const logsHtml = logs.map(log => `
        <div class="bento-card glass-interactive mb-4 animate-stagger-3" style="border-left:4px solid var(--brand-accent);">
            <div class="flex justify-between items-center mb-3" style="flex-wrap:wrap;gap:8px;">
                <h4 style="margin-bottom:0;font-size:1.05rem;">${escapeHtml(log.case_title || log.case_id)}</h4>
                <span class="badge badge-edited font-mono">${log.case_id}</span>
            </div>

            <div style="margin-bottom:12px;">
                <div class="text-xs text-muted font-bold mb-1">RAW AI MODEL DIAGNOSIS</div>
                <div style="color:#ff6b8b;background:rgba(255,51,102,0.12);padding:10px 14px;border-radius:var(--radius-sm);border:1px solid rgba(255,51,102,0.25);font-size:0.92rem;">${escapeHtml(log.ai_diagnosis)}</div>
            </div>

            <div style="margin-bottom:12px;">
                <div class="text-xs text-muted font-bold mb-1">HUMAN CERTIFIED CORRECTION</div>
                <div style="color:#33eb91;background:rgba(0,230,118,0.12);padding:10px 14px;border-radius:var(--radius-sm);border:1px solid rgba(0,230,118,0.25);font-size:0.92rem;">${escapeHtml(log.human_correction)}</div>
            </div>

            <div style="margin-bottom:12px;">
                <div class="text-xs text-muted font-bold mb-1">FAILURE MODE / WHY MODEL WAS INACCURATE</div>
                <div class="text-sm text-secondary">${escapeHtml(log.why_ai_wrong)}</div>
            </div>

            <div style="margin-bottom:12px;">
                <div class="text-xs text-muted font-bold mb-1">FINAL VERIFIED DIAGNOSIS</div>
                <div class="text-sm" style="color:var(--text-primary);font-weight:700;">${escapeHtml(log.final_diagnosis)}</div>
            </div>

            <div>
                <div class="text-xs text-muted font-bold mb-1">CONTINUOUS LEARNING TAKEAWAY</div>
                <div style="color:var(--brand-primary);font-style:italic;background:rgba(0,242,174,0.1);padding:10px 14px;border-radius:var(--radius-sm);border:1px solid rgba(0,242,174,0.25);font-size:0.92rem;">${escapeHtml(log.lesson)}</div>
            </div>
        </div>
    `).join('');

    return `
        <div class="demo-badge glass-pill mb-6" style="border-radius:var(--radius-lg);padding:16px 20px;font-size:0.9rem;display:flex;align-items:center;gap:14px;">
            <span><strong>Responsible AI Protocol Active:</strong> Every automated network inference requires explicit human verification before change execution. The ledger below logs model corrections to preserve diagnostic safety.</span>
        </div>

        ${statsHtml}
        ${formula}

        <h2 style="font-size:1.25rem;margin:30px 0 16px;display:flex;align-items:center;gap:10px;">
            <span>Audited Correction Ledger</span>
            <span class="badge badge-open font-mono">${logs.length} Entries</span>
        </h2>
        ${logsHtml || '<div class="empty-state"><h3>No corrections logged yet</h3></div>'}
    `;
}
