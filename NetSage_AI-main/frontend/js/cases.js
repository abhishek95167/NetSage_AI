/**
 * NetSage AI — Cases List Page
 * Bento-Glass Incident Management & Filter Matrix
 */

async function renderCases() {
    const container = document.getElementById('cases-content');
    try {
        const cases = await api.getCases();
        container.innerHTML = buildCasesHtml(cases);
        initGlassSpotlight();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Failed to load incidents</h3><p>${err.message}</p></div>`;
    }
}

function buildCasesHtml(cases) {
    if (!cases.length) {
        return `
            <div class="empty-state">
                <h3>No incident records found</h3>
                <p>Register your first network telemetry case to begin diagnosis</p>
                <button class="btn btn-primary btn-glow mt-4" onclick="navigateTo('new-case')">Register First Case</button>
            </div>`;
    }

    const filterHtml = `
        <div class="flex gap-3 mb-4 items-center" style="flex-wrap:wrap;">
            <select class="form-select" style="width:auto;min-width:140px;" id="filterStatus" onchange="filterCases()">
                <option value="">Status: All</option>
                <option value="Open">Open</option>
                <option value="Analyzed">Analyzed</option>
                <option value="Resolved">Resolved</option>
                <option value="Rejected">Rejected</option>
            </select>
            <select class="form-select" style="width:auto;min-width:140px;" id="filterConcept" onchange="filterCases()">
                <option value="">Concept: All</option>
                <option value="VLAN">VLAN</option>
                <option value="Gateway">Gateway</option>
                <option value="DHCP">DHCP</option>
                <option value="DNS">DNS</option>
                <option value="Routing">Routing</option>
                <option value="ACL">ACL</option>
                <option value="NAT">NAT</option>
                <option value="Wireless">Wireless</option>
            </select>
            <select class="form-select" style="width:auto;min-width:140px;" id="filterSeverity" onchange="filterCases()">
                <option value="">Severity: All</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
            </select>
            <span class="text-muted text-sm font-mono" style="align-self:center;margin-left:auto;background:rgba(255,255,255,0.05);padding:6px 12px;border-radius:var(--radius-pill);border:1px solid var(--glass-border);">
                ${cases.length} Total Telemetry Records
            </span>
        </div>
    `;

    const rows = cases.map(c => `
        <tr onclick="navigateTo('case-detail', '${c.case_id}')">
            <td style="color:var(--brand-primary);font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;">${c.case_id}</td>
            <td style="color:var(--text-primary);max-width:340px;font-weight:600;" class="truncate">${escapeHtml(c.title)}</td>
            <td>${statusBadge(c.status)}</td>
            <td>${severityBadge(c.severity)}</td>
            <td>${conceptBadge(c.concept)}</td>
            <td>${osiLayerBadge(c.osi_layer)}</td>
            <td class="text-muted text-xs font-mono">${formatDate(c.created_at)}</td>
            <td style="text-align:right;">
                <button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();confirmDeleteCase('${c.case_id}')" title="Delete Incident">Delete</button>
            </td>
        </tr>
    `).join('');

    return `
        ${filterHtml}
        <div class="bento-card glass-interactive animate-stagger-1" style="padding:0;overflow:hidden;">
            <div class="table-container">
                <table id="casesTable">
                    <thead>
                        <tr>
                            <th>Incident ID</th>
                            <th>Title / Topology</th>
                            <th>Status</th>
                            <th>Severity</th>
                            <th>Concept</th>
                            <th>Layer</th>
                            <th>Timestamp</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>${rows}</tbody>
                </table>
            </div>
        </div>
    `;
}

async function filterCases() {
    const status = document.getElementById('filterStatus').value;
    const concept = document.getElementById('filterConcept').value;
    const severity = document.getElementById('filterSeverity').value;

    try {
        const cases = await api.getCases({ status, concept, severity });
        const tbody = document.querySelector('#casesTable tbody');
        if (tbody) {
            tbody.innerHTML = cases.map(c => `
                <tr onclick="navigateTo('case-detail', '${c.case_id}')">
                    <td style="color:var(--brand-primary);font-weight:700;font-family:'JetBrains Mono',monospace;white-space:nowrap;">${c.case_id}</td>
                    <td style="color:var(--text-primary);max-width:340px;font-weight:600;" class="truncate">${escapeHtml(c.title)}</td>
                    <td>${statusBadge(c.status)}</td>
                    <td>${severityBadge(c.severity)}</td>
                    <td>${conceptBadge(c.concept)}</td>
                    <td>${osiLayerBadge(c.osi_layer)}</td>
                    <td class="text-muted text-xs font-mono">${formatDate(c.created_at)}</td>
                    <td style="text-align:right;"><button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();confirmDeleteCase('${c.case_id}')" title="Delete Incident">Delete</button></td>
                </tr>
            `).join('') || '<tr><td colspan="8" class="text-center text-muted" style="padding:30px;">No incidents match the selected filter criteria</td></tr>';
        }
    } catch (err) {
        showToast('Failed to filter incidents', 'error');
    }
}

function confirmDeleteCase(caseId) {
    openModal('Delete Incident Telemetry', 
        `<p style="color:var(--text-secondary);line-height:1.6;">Are you sure you want to permanently delete incident record <strong style="color:var(--text-primary);font-family:'JetBrains Mono',monospace;">${caseId}</strong>? All associated diagnosis telemetry and review history will be removed.</p>`,
        `<button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
         <button class="btn btn-danger" onclick="deleteCase('${caseId}')">Confirm Deletion</button>`
    );
}

async function deleteCase(caseId) {
    try {
        await api.deleteCase(caseId);
        closeModal();
        showToast(`Incident ${caseId} purged from database`, 'success');
        renderCases();
    } catch (err) {
        showToast('Failed to delete incident', 'error');
    }
}
