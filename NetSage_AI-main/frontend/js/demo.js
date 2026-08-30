/**
 * NetSage AI — Demo Mode
 * Interactive Bento-Glass Guided Walkthrough
 */

let demoStep = 0;
const DEMO_CASE_ID = 'CASE-001';
const demoSteps = [
    { title: 'Identify Problem', desc: 'Inspect broken network case: PC1 on VLAN 10 cannot communicate.' },
    { title: 'Examine Telemetry', desc: 'View reported symptoms, network topology, and Cisco CLI outputs.' },
    { title: 'Deterministic Rules', desc: 'Execute deterministic checks to catch common syntax/config faults.' },
    { title: 'AI Dual Inference', desc: 'Submit telemetry to AI engine for evidence-based root cause diagnosis.' },
    { title: 'Review AI Evidence', desc: 'Scrutinize cited evidence items and diagnostic confidence score.' },
    { title: 'Human-in-the-Loop', desc: 'Certify, edit, or reject the AI diagnosis as the human reviewer.' },
    { title: 'Safe Fix Procedures', desc: 'View recommended step-by-step fix commands without auto-execution.' },
    { title: 'Audited Resolution', desc: 'Workflow complete! Case marked resolved with verifiable audit trail.' }
];

function renderDemo() {
    const container = document.getElementById('demo-content');
    demoStep = 0;

    container.innerHTML = `
        <div class="demo-badge glass-pill mb-6" style="border-radius:var(--radius-lg);padding:16px 20px;font-size:0.9rem;display:flex;align-items:center;gap:14px;">
            <span><strong>Guided Troubleshooting Tour:</strong> Walk through a complete NetSage AI diagnostic workflow from symptom ingestion to certified resolution using CASE-001 (Access Port VLAN Mismatch).</span>
        </div>

        <div style="display:grid;grid-template-columns:1fr 2fr;gap:24px;">
            <div>
                <h3 style="font-size:1.1rem;margin-bottom:18px;display:flex;align-items:center;gap:8px;">
                    <span>Workflow Milestones</span>
                </h3>
                <div id="demoStepsList">
                    ${demoSteps.map((s, i) => `
                        <div class="demo-step ${i === 0 ? 'active' : ''}" id="demoStep-${i}" onclick="advanceDemo(${i})">
                            <div class="demo-step-number">${i + 1}</div>
                            <div class="demo-step-content">
                                <h4>${s.title}</h4>
                                <p>${s.desc}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div>
                <div class="bento-card glass-interactive" style="position:sticky;top:100px;">
                    <div class="bento-card-header"><div class="bento-title" id="demoViewTitle">Step 1: Identify Problem</div></div>
                    <div id="demoView">
                        <p class="text-secondary mb-4">Click below or select a milestone to start the interactive tour.</p>
                        <button class="btn btn-primary btn-glow" onclick="advanceDemo(0)">
                            <span>Launch Guided Tour</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    initGlassSpotlight();
}

async function advanceDemo(step) {
    demoStep = step;

    // Update step indicators
    demoSteps.forEach((_, i) => {
        const el = document.getElementById(`demoStep-${i}`);
        if (!el) return;
        el.classList.remove('active', 'completed');
        if (i < step) el.classList.add('completed');
        if (i === step) el.classList.add('active');
    });

    const viewTitle = document.getElementById('demoViewTitle');
    const view = document.getElementById('demoView');

    viewTitle.textContent = `Step ${step + 1}: ${demoSteps[step].title}`;
    view.innerHTML = `
        <div class="spinner-container" style="padding:40px 0;">
            <div class="spinner"></div>
            <p class="loading-text">Processing milestone data...</p>
        </div>`;

    try {
        switch (step) {
            case 0: // Identify problem
                const caseData = await api.getCase(DEMO_CASE_ID);
                view.innerHTML = `
                    <div class="mb-3" style="font-size:1.05rem;">
                        <strong style="color:var(--brand-primary);font-family:'JetBrains Mono',monospace;">${caseData.case_id}</strong>: 
                        <span style="font-weight:700;color:#ffffff;">${escapeHtml(caseData.title)}</span>
                    </div>
                    <div class="flex gap-2 mb-4" style="flex-wrap:wrap;">
                        ${severityBadge(caseData.severity)} ${conceptBadge(caseData.concept)} ${osiLayerBadge(caseData.osi_layer)}
                    </div>
                    <p class="text-secondary mb-4" style="line-height:1.6;">${escapeHtml(caseData.symptom)}</p>
                    <button class="btn btn-primary btn-sm btn-glow" onclick="advanceDemo(1)">Next Milestone → Examine Telemetry</button>
                `;
                break;

            case 1: // Examine telemetry
                const c1 = await api.getCase(DEMO_CASE_ID);
                view.innerHTML = `
                    <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                        <div class="text-xs text-muted font-bold mb-1">REPORTED SYMPTOM</div>
                        <div class="text-sm">${escapeHtml(c1.symptom)}</div>
                    </div>
                    <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                        <div class="text-xs text-muted font-bold mb-1">NETWORK TOPOLOGY</div>
                        <div class="text-sm text-secondary">${escapeHtml(c1.topology_notes)}</div>
                    </div>
                    <div>
                        <div class="text-xs text-muted font-bold mb-2">CISCO SHOW OUTPUTS</div>
                        ${terminalBlock(c1.show_outputs, 'Cisco Packet Tracer CLI')}
                    </div>
                    <button class="btn btn-primary btn-sm btn-glow mt-4" onclick="advanceDemo(2)">Next Milestone → Run Rule Checker</button>
                `;
                break;

            case 2: // Rule Checker
                const ruleResult = await api.runRuleCheck(DEMO_CASE_ID);
                const ruleItems = (ruleResult.results || []).map(r => {
                    const isFail = r.status === 'FAIL';
                    return `
                        <div class="rule-result ${isFail ? 'fail' : 'pass'}" style="display:flex;gap:12px;padding:12px;background:rgba(0,0,0,0.3);border-radius:var(--radius-md);margin-bottom:8px;border-left:3px solid ${isFail ? 'var(--severity-high)' : 'var(--severity-low)'};">
                            <div style="font-size:0.8rem;font-weight:800;padding:2px 6px;border-radius:4px;background:${isFail ? 'rgba(255,51,102,0.2)' : 'rgba(0,230,118,0.2)'};color:${isFail ? '#ff6b8b' : '#33eb91'};align-self:flex-start;">${isFail ? 'FAIL' : 'PASS'}</div>
                            <div>
                                <div style="font-weight:700;font-size:0.9rem;color:#ffffff;">${escapeHtml(r.check.replace(/_/g, ' ').toUpperCase())}</div>
                                <div style="font-size:0.84rem;color:var(--text-secondary);">${escapeHtml(r.message)}</div>
                            </div>
                        </div>`;
                }).join('');
                view.innerHTML = `
                    <p class="text-secondary text-sm mb-3">Deterministic rule heuristics analysis:</p>
                    ${ruleItems}
                    <button class="btn btn-primary btn-sm btn-glow mt-4" onclick="advanceDemo(3)">Next Milestone → Run AI Diagnosis</button>
                `;
                break;

            case 3: // AI Diagnosis
                const diagnosis = await api.runDiagnosis(DEMO_CASE_ID);
                const conf = confidenceLabel(diagnosis.confidence);
                view.innerHTML = `
                    <div class="mb-3">${diagnosis.is_demo_mode ? '<span class="badge badge-analyzed">DEMO INFERENCE</span>' : '<span class="badge badge-resolved">LIVE NEURAL</span>'}</div>
                    <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                        <div class="text-xs text-muted font-bold mb-1">DIAGNOSED ROOT CAUSE</div>
                        <div style="font-size:1.08rem;color:#ffffff;font-weight:700;">${escapeHtml(diagnosis.root_cause)}</div>
                    </div>
                    <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                        <div class="text-xs text-muted font-bold mb-2">INFERENCE CONFIDENCE — <span style="color:var(--brand-primary);">${conf.text} (${diagnosis.confidence}%)</span></div>
                        <div style="height:8px;background:rgba(255,255,255,0.08);border-radius:var(--radius-pill);overflow:hidden;">
                            <div style="height:100%;width:${diagnosis.confidence}%;background:var(--brand-primary);border-radius:var(--radius-pill);"></div>
                        </div>
                    </div>
                    <div>
                        <div class="text-xs text-muted font-bold mb-1">OSI LAYER</div>
                        <div>${osiLayerBadge(diagnosis.osi_layer)}</div>
                    </div>
                    <button class="btn btn-primary btn-sm btn-glow mt-4" onclick="advanceDemo(4)">Next Milestone → Review Evidence</button>
                `;
                break;

            case 4: // Review evidence
                const diag2 = await api.getDiagnosis(DEMO_CASE_ID);
                if (diag2) {
                    const ev = (diag2.evidence || []).map(e => `<li>${escapeHtml(e)}</li>`).join('');
                    view.innerHTML = `
                        <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                            <div class="text-xs text-muted font-bold mb-2">AI EVIDENCE CITED</div>
                            ${ev ? `<ul class="evidence-list" style="padding:0;list-style:none;">${ev}</ul>` : '<span class="text-muted">No evidence cited</span>'}
                        </div>
                        <div>
                            <div class="text-xs text-muted font-bold mb-1">RECOMMENDED DIAGNOSTIC PROBE</div>
                            <div class="font-mono text-sm" style="color:var(--brand-primary);padding:8px 12px;background:rgba(0,0,0,0.3);border-radius:var(--radius-sm);">${escapeHtml(diag2.next_command)}</div>
                        </div>
                        <button class="btn btn-primary btn-sm btn-glow mt-4" onclick="advanceDemo(5)">Next Milestone → Human Review</button>
                    `;
                }
                break;

            case 5: // Human Review
                view.innerHTML = `
                    <div style="padding:10px 0;">
                        <h3 style="color:var(--brand-accent);margin-bottom:12px;font-size:1.1rem;display:flex;align-items:center;gap:8px;">
                            <span>Human-in-the-Loop Sign-Off</span>
                        </h3>
                        <p class="text-secondary text-sm mb-4">Validate or adjust the AI's root-cause determination before proceeding to configuration remediation:</p>
                        <div class="form-group">
                            <label class="form-label">Reviewer Notes</label>
                            <textarea class="form-textarea" id="demoReviewNotes" rows="2" placeholder="Your assessment...">Accurate diagnosis - verified FastEthernet0/5 assigned to VLAN 1 in switchport configuration.</textarea>
                        </div>
                        <div class="flex gap-3" style="flex-wrap:wrap;">
                            <button class="btn btn-success" onclick="demoSubmitReview('accepted')"><span>Accept Analysis</span></button>
                            <button class="btn btn-warning" onclick="demoSubmitReview('edited')"><span>Edit Analysis</span></button>
                            <button class="btn btn-danger" onclick="demoSubmitReview('rejected')"><span>Reject</span></button>
                        </div>
                    </div>
                `;
                break;

            case 6: // Fix recommendation
                const diag3 = await api.getDiagnosis(DEMO_CASE_ID);
                if (diag3) {
                    const fixes = (diag3.fix_steps || []).map(s => `<li>${escapeHtml(s)}</li>`).join('');
                    view.innerHTML = `
                        <div style="margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid var(--glass-border);">
                            <div class="text-xs text-muted font-bold mb-2">REMEDIATION SEQUENCE</div>
                            ${fixes ? `<ol class="fix-steps" style="padding:0;list-style:none;">${fixes}</ol>` : '<span class="text-muted">No fix steps provided</span>'}
                        </div>
                        <div class="demo-badge glass-pill mt-4" style="border-radius:var(--radius-md);">
                            <span><strong>Safety Guardrail:</strong> NetSage AI displays remediation steps for manual engineer execution; commands are never executed directly on switches automatically.</span>
                        </div>
                        <button class="btn btn-primary btn-sm btn-glow mt-4" onclick="advanceDemo(7)">Next Milestone → Audit Trail Complete</button>
                    `;
                }
                break;

            case 7: // Complete
                view.innerHTML = `
                    <div class="text-center" style="padding:28px 16px;">
                        <h3 style="font-size:1.35rem;margin-bottom:8px;color:#ffffff;">Troubleshooting Workflow Certified</h3>
                        <p class="text-secondary text-sm mb-4">You have completed an end-to-end Packet Tracer root-cause diagnosis:</p>
                        <div style="text-align:left;max-width:440px;margin:0 auto;background:rgba(0,0,0,0.3);padding:18px 24px;border-radius:var(--radius-lg);border:1px solid var(--glass-border);">
                            <div class="text-sm text-secondary" style="line-height:2.2;">
                                • Ingested broken network symptom & CLI output<br>
                                • Ran deterministic rule checker<br>
                                • Performed neural evidence-based diagnosis<br>
                                • Human engineer certified & signed off<br>
                                • Immutable Responsible AI audit log recorded
                            </div>
                        </div>
                        <div class="flex gap-3 mt-6" style="justify-content:center;">
                            <button class="btn btn-primary btn-glow" onclick="navigateTo('dashboard')">Return to NOC Dashboard</button>
                            <button class="btn btn-ghost" onclick="renderDemo()">Restart Guided Tour</button>
                        </div>
                    </div>
                `;
                break;
        }
    } catch (err) {
        view.innerHTML = `<div class="empty-state"><h3>Tour Error</h3><p>${err.message}</p></div>`;
    }
}

async function demoSubmitReview(decision) {
    const notes = document.getElementById('demoReviewNotes')?.value || '';
    try {
        await api.submitReview(DEMO_CASE_ID, {
            decision: decision,
            edited_diagnosis: '',
            reviewer_notes: notes
        });
        showToast(`Review recorded: ${decision.toUpperCase()}`, 'success');
        advanceDemo(6);
    } catch (err) {
        showToast(`Review failed: ${err.message}`, 'error');
    }
}
