/**
 * NetSage AI — Main Application Router & Controller
 * Dynamic Island Navigation, Telemetry Ticker, and Glass Spotlight Orchestration
 */

let currentPage = 'dashboard';
let currentCaseId = null;

function navigateTo(page, param = null) {
    currentPage = page;
    currentCaseId = param;

    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));

    // Update dynamic island nav pills
    document.querySelectorAll('.nav-pill').forEach(n => n.classList.remove('active'));
    const navPill = document.querySelector(`.nav-pill[data-page="${page}"]`);
    if (navPill) navPill.classList.add('active');

    // Show target page
    const pageName = page === 'case-detail' ? 'case-detail' : page;
    const pageEl = document.getElementById(`page-${pageName}`);
    if (pageEl) {
        pageEl.classList.remove('hidden');
    }

    // Render target page content
    switch (page) {
        case 'dashboard':
            renderDashboard();
            break;
        case 'cases':
            renderCases();
            break;
        case 'case-detail':
            if (param) renderCaseDetail(param);
            break;
        case 'new-case':
            renderCaseForm();
            break;
        case 'analytics':
            renderAnalytics();
            break;
        case 'responsible-ai':
            renderResponsibleAI();
            break;
        case 'demo':
            renderDemo();
            break;
    }

    // Initialize interactive spotlight on freshly rendered cards
    setTimeout(() => {
        initGlassSpotlight();
    }, 50);

    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Close modal on overlay click
document.getElementById('modalOverlay').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
});

// Live Simulated Network Telemetry Ticker
function initTelemetryTicker() {
    const tickerEl = document.getElementById('tickerLatency');
    if (!tickerEl) return;

    setInterval(() => {
        const baseLatency = 1.1;
        const jitter = (Math.random() * 0.5 - 0.25).toFixed(2);
        const currentLatency = (baseLatency + parseFloat(jitter)).toFixed(1);
        tickerEl.textContent = `RTT: ${currentLatency}ms`;
    }, 3000);
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    // Check health and update mode badge in dynamic island
    api.getHealth().then(health => {
        const badge = document.getElementById('modeBadge');
        const badgeText = document.getElementById('modeBadgeText');
        if (badge && badgeText) {
            if (health.demo_mode) {
                badgeText.textContent = 'Demo Mode Active';
            } else {
                badge.innerHTML = '<span class="status-pulse-dot" style="background:#00e676;box-shadow:0 0 8px #00e676;"></span><span>Live AI Connected</span>';
                badge.style.borderColor = 'rgba(0,230,118,0.4)';
                badge.style.background = 'rgba(0,230,118,0.15)';
                badge.style.color = '#33eb91';
            }
        }
    }).catch(() => {});

    initTelemetryTicker();
    navigateTo('dashboard');
});
