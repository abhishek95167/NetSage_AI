/**
 * NetSage AI — Dashboard Page
 * Futuristic Bento-Glass NOC Dashboard with Interactive Packet Topology Simulator
 */

let dashboardCharts = {};

async function renderDashboard() {
    const container = document.getElementById('dashboard-content');
    try {
        const stats = await api.getDashboardStats();
        container.innerHTML = buildDashboardHtml(stats);
        renderDashboardCharts(stats);
        initGlassSpotlight();
    } catch (err) {
        container.innerHTML = `<div class="empty-state"><h3>Failed to load dashboard</h3><p>${err.message}</p></div>`;
    }
}

function buildDashboardHtml(stats) {
    const totalReviews = stats.accepted_diagnoses + stats.edited_diagnoses + stats.rejected_diagnoses;
    const reviewedPercent = stats.total_cases > 0 ? Math.round((stats.analyzed_cases / stats.total_cases) * 100) : 0;
    const validationPercent = totalReviews > 0 ? Math.round((stats.accepted_diagnoses / totalReviews) * 100) : 0;

    const recentRows = (stats.recent_cases || []).map(c => `
        <tr onclick="navigateTo('case-detail', '${c.case_id}')">
            <td style="color:var(--brand-primary);font-weight:700;font-family:'JetBrains Mono',monospace;">${c.case_id}</td>
            <td style="color:#ffffff;max-width:320px;font-weight:600;" class="truncate">${escapeHtml(c.title)}</td>
            <td>${statusBadge(c.status)}</td>
            <td>${severityBadge(c.severity)}</td>
            <td>${conceptBadge(c.concept)}</td>
            <td>${osiLayerBadge(c.osi_layer)}</td>
            <td class="text-muted text-xs font-mono">${formatDate(c.created_at)}</td>
        </tr>
    `).join('');

    return `
        <!-- Top Holographic Metric Rings Bento Row -->
        <div class="bento-grid animate-stagger-1">
            <div class="bento-col-4">
                ${renderHoloRing(stats.agreement_rate, '#00f2ae', 'AI Alignment Precision', 'Human-in-the-loop consensus score')}
            </div>
            <div class="bento-col-4">
                ${renderHoloRing(reviewedPercent, '#8b5cf6', 'Telemetry Coverage', `${stats.analyzed_cases} of ${stats.total_cases} cases AI diagnosed`)}
            </div>
            <div class="bento-col-4">
                ${renderHoloRing(validationPercent, '#38bdf8', 'Validation Health', `${stats.accepted_diagnoses} verified ground truths`)}
            </div>
        </div>

        <!-- Interactive Packet Tracer Network Topology Lab Visualizer -->
        <div class="mb-6 animate-stagger-2">
            ${renderTopologyLabVisualizer(null, 'dashboardTopologyLab')}
        </div>

        <!-- Bento Grid Charts & Telemetry -->
        <div class="bento-grid animate-stagger-3">
            <!-- Concept Doughnut Chart -->
            <div class="bento-col-4 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">Concept Distribution</div>
                    <span class="badge badge-open">Top Issues</span>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="chartIssueType"></canvas>
                </div>
            </div>

            <!-- Severity Spectrum Bar Chart -->
            <div class="bento-col-4 bento-card glass-interactive">
                <div class="bento-card-header">
                    <div class="bento-title">Incident Severity Spectrum</div>
                    <span class="badge badge-high">NOC Priority</span>
                </div>
                <div style="height:260px;position:relative;">
                    <canvas id="chartSeverity"></canvas>
                </div>
            </div>

            <!-- Quick Telemetry Stat Pods Bento -->
            <div class="bento-col-4" style="display:flex;flex-direction:column;gap:14px;">
                <div class="bento-card glass-interactive" style="padding:16px;">
                    <div class="text-xs text-muted font-bold">TOTAL RECORDED INCIDENTS</div>
                    <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:var(--brand-primary);">${stats.total_cases}</div>
                    <div class="text-xs text-secondary">Packet Tracer lab problems in ledger</div>
                </div>
                <div class="bento-card glass-interactive" style="padding:16px;">
                    <div class="text-xs text-muted font-bold">HUMAN GOVERNANCE REVIEWS</div>
                    <div style="font-family:'Outfit',sans-serif;font-size:2.2rem;font-weight:800;color:#c4b5fd;">${totalReviews}</div>
                    <div class="text-xs text-secondary">${stats.accepted_diagnoses} approved • ${stats.edited_diagnoses} adjusted • ${stats.rejected_diagnoses} flagged</div>
                </div>
            </div>
        </div>

        <!-- Live Troubleshooting Stream Matrix -->
        <div class="bento-card glass-interactive animate-stagger-4" style="padding:0;overflow:hidden;">
            <div class="bento-card-header" style="padding:22px 28px;margin-bottom:0;border-bottom:1px solid var(--glass-border);background:rgba(255,255,255,0.02);">
                <div class="bento-title">Live Packet Tracer Incident Ledger</div>
                <button class="btn btn-ghost btn-sm" onclick="navigateTo('cases')">View Full Incident Center →</button>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Incident ID</th>
                            <th>Topology / Lab Issue</th>
                            <th>Status</th>
                            <th>Severity</th>
                            <th>Concept</th>
                            <th>Layer</th>
                            <th>Recorded</th>
                        </tr>
                    </thead>
                    <tbody>${recentRows || '<tr><td colspan="7" class="text-center text-muted" style="padding:32px;">No incidents recorded yet</td></tr>'}</tbody>
                </table>
            </div>
        </div>
    `;
}

function renderDashboardCharts(stats) {
    Object.values(dashboardCharts).forEach(c => c.destroy());
    dashboardCharts = {};

    const neonPalette = ['#00f2ae', '#8b5cf6', '#ffb800', '#ff3366', '#38bdf8', '#f43f5e', '#00e676', '#00f2fe'];

    // Issue Type Chart (Doughnut)
    const issueCtx = document.getElementById('chartIssueType');
    if (issueCtx) {
        const types = stats.cases_by_type || {};
        dashboardCharts.issueType = new Chart(issueCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(types),
                datasets: [{
                    data: Object.values(types),
                    backgroundColor: neonPalette,
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
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 },
                            padding: 10,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(8, 14, 32, 0.94)',
                        titleColor: '#ffffff',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.18)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 10
                    }
                },
                cutout: '72%'
            }
        });
    }

    // Severity Chart (Bar)
    const sevCtx = document.getElementById('chartSeverity');
    if (sevCtx) {
        const sevs = stats.cases_by_severity || {};
        const sevColors = { 'Critical': '#ff3366', 'High': '#ff8800', 'Medium': '#ffcc00', 'Low': '#00e676' };
        dashboardCharts.severity = new Chart(sevCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(sevs),
                datasets: [{
                    data: Object.values(sevs),
                    backgroundColor: Object.keys(sevs).map(s => sevColors[s] || '#8b5cf6'),
                    borderRadius: 8,
                    borderSkipped: false,
                    maxBarThickness: 46
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(8, 14, 32, 0.94)',
                        titleColor: '#ffffff',
                        bodyColor: '#94a3b8',
                        borderColor: 'rgba(255, 255, 255, 0.18)',
                        borderWidth: 1,
                        padding: 12,
                        cornerRadius: 10
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 600 } },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: '#64748b', stepSize: 1, font: { family: 'JetBrains Mono' } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        border: { dash: [4, 4] }
                    }
                }
            }
        });
    }
}
