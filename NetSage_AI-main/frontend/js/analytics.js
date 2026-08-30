/**
 * NetSage AI — Analytics Page
 * Metrics charts, accuracy tracking, and telemetry visualizations.
 */

let analyticsCharts = {};

async function renderAnalytics() {
    const container = document.getElementById('analytics-content');
    try {
        const data = await api.getAnalytics();
        const stats = await api.getDashboardStats();
        container.innerHTML = buildAnalyticsHtml(data, stats);
        renderAnalyticsCharts(data);
        initGlassSpotlight();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Failed to load telemetry analytics</h3><p>${err.message}</p></div>`;
    }
}

function buildAnalyticsHtml(data, stats) {
    return `
        <!-- Top Holographic Metric Rings Bento Row -->
        <div class="bento-grid animate-stagger-1">
            <div class="bento-col-4">
                ${renderHoloRing(stats.agreement_rate, '#00f2ae', 'AI Alignment Precision', 'Human-in-the-loop consensus score')}
            </div>
            <div class="bento-col-4">
                ${renderHoloRing(Math.round((stats.analyzed_cases / (stats.total_cases || 1)) * 100), '#8b5cf6', 'Telemetry Coverage', `${stats.analyzed_cases} of ${stats.total_cases} cases AI diagnosed`)}
            </div>
            <div class="bento-col-4">
                ${renderHoloRing(Math.round((stats.accepted_diagnoses / ((stats.accepted_diagnoses + stats.edited_diagnoses + stats.rejected_diagnoses) || 1)) * 100), '#38bdf8', 'Validation Health', `${stats.accepted_diagnoses} verified ground truths`)}
            </div>
        </div>

        <div class="bento-grid animate-stagger-2">
            <div class="bento-col-6 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">Issue Concept Distribution</div>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="analyticsIssueChart"></canvas>
                </div>
            </div>
            <div class="bento-col-6 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">AI vs Human Decision Consensus</div>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="analyticsDecisionChart"></canvas>
                </div>
            </div>
        </div>

        <div class="bento-grid animate-stagger-3">
            <div class="bento-col-6 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">Incidents by OSI Layer</div>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="analyticsOsiChart"></canvas>
                </div>
            </div>
            <div class="bento-col-6 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">Severity Distribution Breakdown</div>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="analyticsSevChart"></canvas>
                </div>
            </div>
        </div>

        <div class="bento-card glass-interactive animate-stagger-4" style="padding:0;overflow:hidden;">
            <div class="bento-card-header" style="padding:20px 24px;margin-bottom:0;border-bottom:1px solid var(--glass-border);background:rgba(255,255,255,0.02);">
                <div class="bento-title">Most Recurring Root Causes in Telemetry</div>
            </div>
            <div class="table-container">
                <table>
                    <thead><tr><th>Identified Root Cause</th><th>Occurrences</th></tr></thead>
                    <tbody>
                        ${(data.common_root_causes || []).map(r => `
                            <tr>
                                <td style="color:var(--text-primary);font-weight:600;">${escapeHtml(r.cause)}</td>
                                <td><span class="badge badge-analyzed" style="font-family:'JetBrains Mono',monospace;">${r.count} incidents</span></td>
                            </tr>
                        `).join('') || '<tr><td colspan="2" class="text-center text-muted" style="padding:30px;">No telemetry records available</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderAnalyticsCharts(data) {
    Object.values(analyticsCharts).forEach(c => c.destroy());
    analyticsCharts = {};

    const neonPalette = ['#00f2ae', '#8b5cf6', '#ffb800', '#ff3366', '#38bdf8', '#f43f5e', '#00e676', '#00f2fe'];

    // Issue type chart (Polar)
    const issueCtx = document.getElementById('analyticsIssueChart');
    if (issueCtx && data.issue_types?.length) {
        analyticsCharts.issue = new Chart(issueCtx, {
            type: 'polarArea',
            data: {
                labels: data.issue_types.map(i => i.name),
                datasets: [{
                    data: data.issue_types.map(i => i.count),
                    backgroundColor: neonPalette.map(c => c + '66'),
                    borderColor: neonPalette,
                    borderWidth: 1.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 }, padding: 12 }
                    }
                },
                scales: {
                    r: {
                        ticks: { display: false },
                        grid: { color: 'rgba(255, 255, 255, 0.08)' }
                    }
                }
            }
        });
    }

    // Decision chart (Doughnut)
    const decCtx = document.getElementById('analyticsDecisionChart');
    if (decCtx && data.ai_vs_human?.length) {
        const decColors = { accepted: '#00e676', edited: '#ffb800', rejected: '#ff3366' };
        analyticsCharts.decision = new Chart(decCtx, {
            type: 'doughnut',
            data: {
                labels: data.ai_vs_human.map(d => d.name.charAt(0).toUpperCase() + d.name.slice(1)),
                datasets: [{
                    data: data.ai_vs_human.map(d => d.count),
                    backgroundColor: data.ai_vs_human.map(d => decColors[d.name] || '#8b5cf6'),
                    borderColor: 'rgba(8, 14, 30, 0.9)',
                    borderWidth: 3,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 }, padding: 14 }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // OSI layer chart (Horizontal Bar)
    const osiCtx = document.getElementById('analyticsOsiChart');
    if (osiCtx && data.osi_layers?.length) {
        const osiColors = { 'Layer 1': '#f43f5e', 'Layer 2': '#fb923c', 'Layer 3': '#38bdf8', 'Layer 4': '#a855f7', 'Layer 7': '#00f2fe' };
        analyticsCharts.osi = new Chart(osiCtx, {
            type: 'bar',
            data: {
                labels: data.osi_layers.map(o => o.name),
                datasets: [{
                    data: data.osi_layers.map(o => o.count),
                    backgroundColor: data.osi_layers.map(o => osiColors[o.name] || '#8b5cf6'),
                    borderRadius: 6,
                    maxBarThickness: 38
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        ticks: { color: '#64748b', stepSize: 1, font: { family: 'JetBrains Mono' } },
                        grid: { color: 'rgba(255, 255, 255, 0.04)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 600 } },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // Severity chart (Doughnut)
    const sevCtx = document.getElementById('analyticsSevChart');
    if (sevCtx && data.severity_distribution?.length) {
        const sevColors = { 'Critical': '#ff3366', 'High': '#ff8800', 'Medium': '#ffcc00', 'Low': '#00e676' };
        analyticsCharts.sev = new Chart(sevCtx, {
            type: 'doughnut',
            data: {
                labels: data.severity_distribution.map(s => s.name),
                datasets: [{
                    data: data.severity_distribution.map(s => s.count),
                    backgroundColor: data.severity_distribution.map(s => sevColors[s.name] || '#8b5cf6'),
                    borderColor: 'rgba(8, 14, 30, 0.9)',
                    borderWidth: 3,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 }, padding: 12 }
                    }
                },
                cutout: '68%'
            }
        });
    }
}
