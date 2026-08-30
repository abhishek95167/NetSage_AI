/**
 * NetSage AI — Reusable Components & Visualizers Engine
 * Interactive Packet Tracer Topology Simulator, Command Palette, Holographic Rings & Inspector
 */

// --- Cursor Spotlight Event Handler ---
function initGlassSpotlight() {
    document.querySelectorAll('.glass-interactive, .bento-card, .holo-metric-card').forEach(card => {
        card.addEventListener('mousemove', e => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

// --- Holographic Circular Metric Ring Generator ---
function renderHoloRing(percent, colorHex, label, subtext, size = 78) {
    const radius = 33;
    const circumference = 2 * Math.PI * radius;
    const validPercent = Math.min(100, Math.max(0, percent || 0));
    const strokeDashoffset = circumference - (validPercent / 100) * circumference;

    return `
        <div class="holo-metric-card glass-interactive">
            <svg class="holo-ring-svg" viewBox="0 0 80 80" style="width:${size}px;height:${size}px;">
                <circle class="holo-ring-bg" cx="40" cy="40" r="${radius}"></circle>
                <circle class="holo-ring-fill" cx="40" cy="40" r="${radius}" 
                    stroke="${colorHex}" 
                    stroke-dasharray="${circumference}" 
                    stroke-dashoffset="${strokeDashoffset}"
                    style="color:${colorHex};">
                </circle>
            </svg>
            <div class="holo-metric-info">
                <div class="holo-metric-label">${label}</div>
                <div class="holo-metric-value">${validPercent}%</div>
                <div class="holo-metric-sub">${subtext}</div>
            </div>
        </div>`;
}

// --- Interactive Cisco Packet Tracer Network Topology Lab Simulator ---
let topologyAnimInterval = null;

function renderTopologyLabVisualizer(faultConcept = null, containerId = 'topologyLab') {
    const isVlanFault = faultConcept === 'VLAN' || faultConcept === 'Layer 2';
    const isGatewayFault = faultConcept === 'Gateway' || faultConcept === 'Routing' || faultConcept === 'Layer 3';
    const isFault = Boolean(faultConcept);

    return `
        <div class="topology-lab-box glass-interactive" id="${containerId}">
            <div class="topology-controls">
                <div class="bento-title">
                    <span>Cisco Packet Tracer Topology Lab Simulator</span>
                    <span class="badge ${isFault ? 'badge-high' : 'badge-low'}" style="margin-left:8px;">
                        ${isFault ? 'Fault Isolated in Segment' : 'All Paths Live'}
                    </span>
                </div>
                <div class="flex gap-2 items-center">
                    <button class="btn btn-primary btn-sm" onclick="simulatePacketFlow('${containerId}', '${faultConcept || ''}')">
                        <span>Simulate Ping Trace</span>
                    </button>
                    <button class="btn btn-ghost btn-sm" onclick="resetTopologySimulation('${containerId}')">Reset</button>
                </div>
            </div>

            <div class="topology-interactive-canvas">
                <svg class="topology-svg" viewBox="0 0 900 180" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="linkGradHealthy" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stop-color="#00f2ae" stop-opacity="0.8"/>
                            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.8"/>
                        </linearGradient>
                        <linearGradient id="linkGradBroken" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stop-color="#ffb800"/>
                            <stop offset="100%" stop-color="#ff3366"/>
                        </linearGradient>
                    </defs>

                    <!-- Link 1: PC-1 to Access Switch SW-1 -->
                    <line x1="100" y1="90" x2="275" y2="90" 
                        class="topology-link ${isVlanFault ? 'fault' : 'active'}" 
                        id="${containerId}_link1"
                        stroke="${isVlanFault ? 'url(#linkGradBroken)' : 'url(#linkGradHealthy)'}" />

                    <!-- Link 2: SW-1 to Core Router R1 -->
                    <line x1="275" y1="90" x2="450" y2="90" 
                        class="topology-link ${isGatewayFault ? 'fault' : 'active'}" 
                        id="${containerId}_link2"
                        stroke="${isGatewayFault ? 'url(#linkGradBroken)' : 'url(#linkGradHealthy)'}" />

                    <!-- Link 3: R1 to Firewall FW-1 -->
                    <line x1="450" y1="90" x2="625" y2="90" 
                        class="topology-link active" 
                        id="${containerId}_link3"
                        stroke="url(#linkGradHealthy)" />

                    <!-- Link 4: FW-1 to Server DB -->
                    <line x1="625" y1="90" x2="800" y2="90" 
                        class="topology-link active" 
                        id="${containerId}_link4"
                        stroke="url(#linkGradHealthy)" />

                    <!-- Animated Flying Packet Particle -->
                    <circle cx="100" cy="90" r="7" class="packet-particle" id="${containerId}_packet" style="display:none;"></circle>

                    <!-- Node 1: Workstation PC-1 -->
                    <g class="topology-node" transform="translate(100, 90)" onclick="openNodeInspector('PC1')">
                        <circle class="node-bg node-active" r="32"></circle>
                        <text y="-5">PC-1</text>
                        <text y="14" class="node-sub">VLAN 10 • .10.15</text>
                    </g>

                    <!-- Node 2: Access Switch SW-1 -->
                    <g class="topology-node" transform="translate(275, 90)" onclick="openNodeInspector('SW1')">
                        <circle class="node-bg ${isVlanFault ? 'node-fault' : 'node-active'}" r="34"></circle>
                        <text y="-5">SW-1</text>
                        <text y="14" class="node-sub">${isVlanFault ? 'VLAN Port Error' : 'Cat 2960'}</text>
                    </g>

                    <!-- Node 3: Core Router R1 -->
                    <g class="topology-node" transform="translate(450, 90)" onclick="openNodeInspector('R1')">
                        <circle class="node-bg ${isGatewayFault ? 'node-fault' : 'node-active'}" r="34"></circle>
                        <text y="-5">R1-Core</text>
                        <text y="14" class="node-sub">${isGatewayFault ? 'Gateway Mismatch' : 'ISR 4321'}</text>
                    </g>

                    <!-- Node 4: Firewall FW-1 -->
                    <g class="topology-node" transform="translate(625, 90)" onclick="openNodeInspector('FW1')">
                        <circle class="node-bg node-active" r="32"></circle>
                        <text y="-5">FW-1</text>
                        <text y="14" class="node-sub">ASA 5506-X</text>
                    </g>

                    <!-- Node 5: Database Server -->
                    <g class="topology-node" transform="translate(800, 90)" onclick="openNodeInspector('SRV')">
                        <circle class="node-bg node-active" r="32"></circle>
                        <text y="-5">SRV-DB</text>
                        <text y="14" class="node-sub">192.168.20.100</text>
                    </g>
                </svg>
            </div>
            <div class="text-xs text-muted text-center mt-4">
                Tip: Click any node (PC-1, SW-1, R1-Core, FW-1, SRV) to inspect interface telemetry and VLAN configurations.
            </div>
        </div>`;
}

// --- Live Ping Packet Simulation Animation ---
function simulatePacketFlow(containerId, faultConcept) {
    const packet = document.getElementById(`${containerId}_packet`);
    if (!packet) return;

    packet.style.display = 'block';
    packet.setAttribute('class', 'packet-particle');
    
    let currentX = 100;
    const targetX = faultConcept === 'VLAN' ? 275 : (faultConcept === 'Gateway' ? 450 : 800);
    const hasError = Boolean(faultConcept);

    if (topologyAnimInterval) clearInterval(topologyAnimInterval);

    topologyAnimInterval = setInterval(() => {
        currentX += 8;
        packet.setAttribute('cx', currentX);

        if (currentX >= targetX) {
            clearInterval(topologyAnimInterval);
            if (hasError) {
                packet.setAttribute('class', 'packet-particle error');
                showToast(`Packet Drop detected at ${faultConcept === 'VLAN' ? 'Switch SW-1 (VLAN Tag Mismatch)' : 'Router R1 (Gateway / Route Drop)'}`, 'error');
            } else {
                showToast('Ping Trace Complete: 4 packets transmitted, 4 received (0% loss, 1.1ms RTT)', 'success');
            }
        }
    }, 16);
}

function resetTopologySimulation(containerId) {
    if (topologyAnimInterval) clearInterval(topologyAnimInterval);
    const packet = document.getElementById(`${containerId}_packet`);
    if (packet) {
        packet.style.display = 'none';
        packet.setAttribute('cx', 100);
    }
}

// --- Node Telemetry Inspector Data & Popover ---
const nodeData = {
    'PC1': {
        name: 'Workstation PC-1',
        type: 'End Device',
        ip: '192.168.10.15',
        subnet: '255.255.255.0 (/24)',
        gateway: '192.168.10.1',
        mac: '0050.7966.6801',
        vlan: 'VLAN 10 (Sales)',
        interface: 'FastEthernet0 (Up/Up)'
    },
    'SW1': {
        name: 'Cisco Catalyst 2960 (SW-1)',
        type: 'Layer 2 Switch',
        ip: '192.168.10.2 (Management)',
        mac: '0001.9654.4321',
        ports: [
            { port: 'Fa0/1', vlan: '10', status: 'Up/Up', duplex: 'Full', speed: '100Mbps' },
            { port: 'Fa0/2', vlan: '20', status: 'Up/Up', duplex: 'Full', speed: '100Mbps' },
            { port: 'Gi0/1', vlan: 'Trunk (802.1Q)', status: 'Up/Up', duplex: 'Full', speed: '1000Mbps' }
        ]
    },
    'R1': {
        name: 'Cisco ISR 4321 (R1-Core)',
        type: 'Layer 3 Core Router',
        routing: 'OSPF Process 1, Area 0',
        interfaces: [
            { iface: 'Gi0/0/0.10', ip: '192.168.10.1/24', vlan: '10 (Encapsulation 802.1Q)', status: 'Up/Up' },
            { iface: 'Gi0/0/0.20', ip: '192.168.20.1/24', vlan: '20 (Encapsulation 802.1Q)', status: 'Up/Up' },
            { iface: 'Gi0/0/1', ip: '10.0.0.1/30', role: 'WAN Uplink', status: 'Up/Up' }
        ]
    },
    'FW1': {
        name: 'Cisco ASA 5506-X (FW-1)',
        type: 'Stateful Firewall',
        securityLevels: 'Inside: 100, Outside: 0, DMZ: 50',
        inspections: 'HTTP, DNS, ICMP, TCP state'
    },
    'SRV': {
        name: 'Database Cluster SRV-DB',
        type: 'Application Host',
        ip: '192.168.20.100',
        subnet: '255.255.255.0 (/24)',
        gateway: '192.168.20.1',
        services: 'PostgreSQL:5432, HTTPS:443'
    }
};

function openNodeInspector(nodeId) {
    const node = nodeData[nodeId];
    if (!node) return;

    let contentHtml = `
        <div class="flex justify-between items-center mb-4">
            <h3 style="color:#ffffff;font-size:1.2rem;display:flex;align-items:center;gap:10px;">
                <span>${escapeHtml(node.name)}</span>
            </h3>
            <span class="badge badge-open">${escapeHtml(node.type)}</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px;">
            ${node.ip ? `<div class="bento-card" style="padding:12px;"><div class="text-xs text-muted">IP ADDRESS</div><div class="font-mono text-sm" style="color:var(--brand-primary);">${node.ip}</div></div>` : ''}
            ${node.gateway ? `<div class="bento-card" style="padding:12px;"><div class="text-xs text-muted">DEFAULT GATEWAY</div><div class="font-mono text-sm">${node.gateway}</div></div>` : ''}
            ${node.vlan ? `<div class="bento-card" style="padding:12px;"><div class="text-xs text-muted">VLAN ASSIGNMENT</div><div class="text-sm" style="color:var(--brand-accent);">${node.vlan}</div></div>` : ''}
            ${node.routing ? `<div class="bento-card" style="padding:12px;"><div class="text-xs text-muted">ROUTING PROTOCOL</div><div class="text-sm">${node.routing}</div></div>` : ''}
        </div>
    `;

    if (node.ports) {
        contentHtml += `
            <div class="text-xs text-muted font-bold mb-2">INTERFACE SWITCHPORT TABLE</div>
            <div class="table-container mb-4">
                <table>
                    <thead><tr><th>Port</th><th>VLAN</th><th>Status</th><th>Speed</th></tr></thead>
                    <tbody>
                        ${node.ports.map(p => `<tr><td class="font-mono" style="color:var(--brand-primary);">${p.port}</td><td>${p.vlan}</td><td><span class="badge badge-low">${p.status}</span></td><td>${p.speed}</td></tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
    }

    if (node.interfaces) {
        contentHtml += `
            <div class="text-xs text-muted font-bold mb-2">ROUTER INTERFACE TABLE</div>
            <div class="table-container mb-4">
                <table>
                    <thead><tr><th>Interface</th><th>IP / Subnet</th><th>Status</th></tr></thead>
                    <tbody>
                        ${node.interfaces.map(i => `<tr><td class="font-mono" style="color:var(--brand-primary);">${i.iface}</td><td class="font-mono">${i.ip}</td><td><span class="badge badge-low">${i.status}</span></td></tr>`).join('')}
                    </tbody>
                </table>
            </div>`;
    }

    contentHtml += `
        <div class="flex justify-between items-center mt-4">
            <button class="btn btn-secondary btn-sm" onclick="closeNodeInspector()">Close Inspector</button>
        </div>`;

    document.getElementById('nodeInspectorCard').innerHTML = contentHtml;
    document.getElementById('nodeInspectorOverlay').classList.add('active');
}

function closeNodeInspector(e) {
    if (!e || e.target.id === 'nodeInspectorOverlay' || !e.target) {
        document.getElementById('nodeInspectorOverlay').classList.remove('active');
    }
}

// --- Command Palette (Ctrl+K) Controller ---
let allCasesCache = [];

function openCommandPalette() {
    const overlay = document.getElementById('cmdPaletteOverlay');
    const input = document.getElementById('cmdPaletteInput');
    overlay.classList.add('active');
    input.value = '';
    input.focus();

    if (allCasesCache.length === 0) {
        api.getCases().then(cases => {
            allCasesCache = cases || [];
            renderCommandPalette('');
        }).catch(() => {});
    } else {
        renderCommandPalette('');
    }
}

function closeCommandPalette() {
    document.getElementById('cmdPaletteOverlay').classList.remove('active');
}

function renderCommandPalette(query) {
    const container = document.getElementById('cmdPaletteResults');
    const q = (query || '').toLowerCase().trim();

    const quickCommands = [
        { name: 'Dashboard Overview', action: "navigateTo('dashboard')" },
        { name: 'Incident Ledger', action: "navigateTo('cases')" },
        { name: 'Register Incident Case', action: "navigateTo('new-case')" },
        { name: 'Telemetry Analytics', action: "navigateTo('analytics')" },
        { name: 'Responsible AI Governance', action: "navigateTo('responsible-ai')" },
        { name: 'Guided Troubleshooting Tour', action: "navigateTo('demo')" }
    ];

    let matches = quickCommands.filter(cmd => cmd.name.toLowerCase().includes(q));

    let caseMatches = allCasesCache.filter(c => 
        c.case_id.toLowerCase().includes(q) || 
        c.title.toLowerCase().includes(q) || 
        (c.concept && c.concept.toLowerCase().includes(q))
    );

    let html = '';
    if (matches.length > 0) {
        html += '<div class="text-xs text-muted font-bold" style="padding:8px 12px;">SYSTEM NAVIGATION</div>';
        html += matches.map(m => `
            <div class="cmd-item" onclick="${m.action}; closeCommandPalette();">
                <div class="cmd-item-left"><span>${escapeHtml(m.name)}</span></div>
                <span class="text-xs text-muted font-mono">Jump</span>
            </div>
        `).join('');
    }

    if (caseMatches.length > 0) {
        html += '<div class="text-xs text-muted font-bold" style="padding:14px 12px 6px;">MATCHING INCIDENTS</div>';
        html += caseMatches.slice(0, 5).map(c => `
            <div class="cmd-item" onclick="navigateTo('case-detail', '${c.case_id}'); closeCommandPalette();">
                <div class="cmd-item-left">
                    <span class="badge badge-open font-mono">${c.case_id}</span>
                    <span class="truncate" style="max-width:340px;">${escapeHtml(c.title)}</span>
                </div>
                <div class="cmd-item-desc">${c.concept || 'Network'} • ${c.severity}</div>
            </div>
        `).join('');
    }

    if (!html) {
        html = '<div class="text-center text-muted" style="padding:28px;">No matching commands or incidents found</div>';
    }

    container.innerHTML = html;
}

// --- Global Keydown for Command Palette ---
document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        openCommandPalette();
    }
    if (e.key === 'Escape') {
        closeCommandPalette();
        closeNodeInspector();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const cmdInput = document.getElementById('cmdPaletteInput');
    if (cmdInput) {
        cmdInput.addEventListener('input', e => {
            renderCommandPalette(e.target.value);
        });
    }
});

// --- Badges & Utility Helpers ---
function severityBadge(severity) {
    const s = (severity || 'Medium').toLowerCase();
    return `<span class="badge badge-${s}"><span class="status-pulse-dot" style="width:6px;height:6px;"></span>${severity || 'Medium'}</span>`;
}

function statusBadge(status) {
    const s = (status || 'Open').toLowerCase();
    return `<span class="badge badge-${s}">${status || 'Open'}</span>`;
}

function decisionBadge(decision) {
    const d = (decision || '').toLowerCase();
    return `<span class="badge badge-${d}">${decision}</span>`;
}

function osiLayerBadge(layer) {
    if (!layer) return '';
    const l = layer.toLowerCase();
    let cls = 'badge-layer3';
    if (l.includes('1')) cls = 'badge-layer1';
    else if (l.includes('2')) cls = 'badge-layer2';
    else if (l.includes('4')) cls = 'badge-layer4';
    else if (l.includes('7')) cls = 'badge-layer7';
    return `<span class="badge ${cls}">${layer}</span>`;
}

function conceptBadge(concept) {
    if (!concept) return '';
    const colors = {
        'VLAN': '#fb923c', 'Gateway': '#38bdf8', 'DHCP': '#c084fc',
        'DNS': '#00f2fe', 'Routing': '#00f2ae', 'ACL': '#ff3366',
        'NAT': '#f43f5e', 'Wireless': '#ffb800'
    };
    const color = colors[concept] || '#94a3b8';
    return `<span class="badge" style="background:${color}24;color:${color};border:1px solid ${color}66;box-shadow:0 0 14px ${color}33;">${concept}</span>`;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(120%) scale(0.9)';
        toast.style.transition = 'all 0.35s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => toast.remove(), 350);
    }, 4200);
}

function openModal(title, bodyHtml, footerHtml = '') {
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalBody').innerHTML = bodyHtml;
    document.getElementById('modalFooter').innerHTML = footerHtml;
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
}

function confidenceLabel(confidence) {
    if (confidence >= 85) return { text: 'High Confidence', cls: 'confidence-high' };
    if (confidence >= 60) return { text: 'Medium Confidence', cls: 'confidence-medium' };
    return { text: 'Low Confidence', cls: 'confidence-low' };
}

function terminalBlock(content, title = 'Cisco IOS CLI Telemetry') {
    const id = 'term_' + Math.random().toString(36).substring(2, 9);
    return `
        <div class="terminal-wrapper">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <span class="terminal-dot red"></span>
                    <span class="terminal-dot yellow"></span>
                    <span class="terminal-dot green"></span>
                    <span class="terminal-title">${title}</span>
                </div>
                <button class="terminal-copy-btn" onclick="copyTerminalText('${id}', this)">Copy CLI</button>
            </div>
            <div class="terminal" id="${id}">${escapeHtml(content)}</div>
        </div>`;
}

function copyTerminalText(elementId, btn) {
    const el = document.getElementById(elementId);
    if (!el) return;
    navigator.clipboard.writeText(el.textContent).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'Copied';
        btn.style.borderColor = 'var(--brand-primary)';
        btn.style.color = 'var(--brand-primary)';
        setTimeout(() => {
            btn.textContent = orig;
            btn.style.borderColor = '';
            btn.style.color = '';
        }, 2000);
    }).catch(() => {
        showToast('Failed to copy to clipboard', 'error');
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr + (dateStr.endsWith('Z') ? '' : 'Z'));
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
        return dateStr;
    }
}

function formatDateTime(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr + (dateStr.endsWith('Z') ? '' : 'Z'));
        return d.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateStr;
    }
}
