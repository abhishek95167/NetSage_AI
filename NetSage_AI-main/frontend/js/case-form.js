/**
 * NetSage AI — Case Creation Form
 * Bento-Glass Incident Registration with Quick Presets
 */

const PRESET_TEMPLATES = {
    vlan: {
        title: "PC1 in HR Dept Cannot Access Database in Finance VLAN 20",
        symptom: "PC1 (192.168.10.15) cannot ping Finance Server (192.168.20.100). Inter-VLAN routing is enabled on Core Switch SW-1.",
        topology: "Switch SW-1 (Catalyst 3560) connected via trunk Fa0/1 to Access Switch SW-2 (Catalyst 2960). PC1 on SW-2 Fa0/5 in VLAN 10.",
        show_outputs: `SW-1# show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Fa0/1       on               802.1q         trunking      1

Port        Vlans allowed on trunk
Fa0/1       1-4094

Port        Vlans allowed and active in management domain
Fa0/1       1,10,20

SW-2# show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
10   HR                               active    
20   Finance                          active    Fa0/6, Fa0/7

SW-2# show running-config interface FastEthernet 0/5
interface FastEthernet0/5
 switchport mode access
 switchport access vlan 1
!
`,
        expected_fault: "Access port FastEthernet0/5 assigned to default VLAN 1 instead of VLAN 10",
        concept: "VLAN",
        osi_layer: "Layer 2",
        severity: "High"
    },
    gateway: {
        title: "Workstation Offline After DHCP Renewal - Gateway Unreachable",
        symptom: "User reports no internet or LAN connectivity after rebooting PC-4. Pings to 8.8.8.8 fail with 'Destination host unreachable'.",
        topology: "Router R1 (192.168.1.1) is default gateway. PC-4 connected to Switch SW-1 port Gi0/2.",
        show_outputs: `PC-4> ipconfig
FastEthernet0 Connection:
   IP Address......................: 192.168.1.104
   Subnet Mask.....................: 255.255.255.0
   Default Gateway.................: 192.168.1.254

PC-4> ping 192.168.1.1
Pinging 192.168.1.1 with 32 bytes of data:
Reply from 192.168.1.104: Destination host unreachable.

R1# show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES manual up                    up
`,
        expected_fault: "Incorrect default gateway IP 192.168.1.254 configured instead of router IP 192.168.1.1",
        concept: "Gateway",
        osi_layer: "Layer 3",
        severity: "Critical"
    },
    ospf: {
        title: "Branch Office Router R2 Not Receiving OSPF Routes from Headquarters",
        symptom: "Subnets behind Headquarters Router R1 cannot communicate with Branch R2 subnets. Routing table on R2 is empty.",
        topology: "R1 and R2 connected over point-to-point link 10.0.0.0/30 on Serial0/1/0. OSPF Area 0 configured.",
        show_outputs: `R1# show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
(No neighbors listed)

R1# show ip ospf interface Serial0/1/0
Serial0/1/0 is up, line protocol is up
  Internet Address 10.0.0.1/30, Area 0, Attached via Interface Enable
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5

R2# show ip ospf interface Serial0/1/0
Serial0/1/0 is up, line protocol is up
  Internet Address 10.0.0.2/30, Area 1, Attached via Interface Enable
  Timer intervals configured, Hello 10, Dead 40, Wait 40, Retransmit 5
`,
        expected_fault: "OSPF Area mismatch: R1 is in Area 0 while R2 is configured in Area 1",
        concept: "Routing",
        osi_layer: "Layer 3",
        severity: "Critical"
    }
};

function renderCaseForm() {
    const container = document.getElementById('new-case-content');
    container.innerHTML = `
        <div class="bento-card glass-interactive animate-stagger-1" style="max-width:880px;margin:0 auto;">
            <div class="bento-card-header">
                <div class="bento-title">Register Incident Telemetry</div>
            </div>
            <div>
                <div style="margin-bottom:20px;">
                    <label class="form-label">Preset Topologies & Scenarios</label>
                    <div class="quick-fill-container">
                        <button type="button" class="preset-chip" onclick="applyPreset('vlan')">VLAN Port Mismatch</button>
                        <button type="button" class="preset-chip" onclick="applyPreset('gateway')">Wrong Default Gateway</button>
                        <button type="button" class="preset-chip" onclick="applyPreset('ospf')">OSPF Area Mismatch</button>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Incident Title *</label>
                    <input class="form-input" id="caseTitle" type="text" placeholder="e.g., PC Cannot Reach Server in VLAN 30" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Observed Symptom *</label>
                    <textarea class="form-textarea" id="caseSymptom" rows="3" placeholder="Describe the symptom (e.g. Ping timeouts, packet loss, unreachable subnet)..." style="font-family:'Plus Jakarta Sans',sans-serif;" required></textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Topology Notes & Physical Cabling</label>
                    <textarea class="form-textarea" id="caseTopology" rows="3" placeholder="Describe routers, switches, interfaces, subnets, and VLANs..." style="font-family:'Plus Jakarta Sans',sans-serif;"></textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Cisco CLI Show Command Outputs</label>
                    <textarea class="form-textarea" id="caseShowOutputs" rows="8" placeholder="Paste Cisco IOS CLI output here (e.g., show ip int brief, show running-config, show vlan brief)..."></textarea>
                </div>

                <div class="form-group">
                    <label class="form-label">Expected Fault / Ground Truth (Optional)</label>
                    <input class="form-input" id="caseExpectedFault" type="text" placeholder="Ground truth root cause for validation benchmarks">
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:16px;margin-bottom:20px;">
                    <div class="form-group" style="margin-bottom:0;">
                        <label class="form-label">Network Concept</label>
                        <select class="form-select" id="caseConcept">
                            <option value="">Select Concept...</option>
                            <option value="VLAN">VLAN</option>
                            <option value="Gateway">Gateway</option>
                            <option value="DHCP">DHCP</option>
                            <option value="DNS">DNS</option>
                            <option value="Routing">Routing</option>
                            <option value="ACL">ACL</option>
                            <option value="NAT">NAT</option>
                            <option value="Wireless">Wireless</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label class="form-label">OSI Layer</label>
                        <select class="form-select" id="caseOsiLayer">
                            <option value="">Select OSI Layer...</option>
                            <option value="Layer 1">Layer 1 — Physical</option>
                            <option value="Layer 2">Layer 2 — Data Link</option>
                            <option value="Layer 3">Layer 3 — Network</option>
                            <option value="Layer 4">Layer 4 — Transport</option>
                            <option value="Layer 7">Layer 7 — Application</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom:0;">
                        <label class="form-label">Severity Level</label>
                        <select class="form-select" id="caseSeverity">
                            <option value="Medium">Medium</option>
                            <option value="Low">Low</option>
                            <option value="High">High</option>
                            <option value="Critical">Critical</option>
                        </select>
                    </div>
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:12px;margin-top:20px;padding-top:20px;border-top:1px solid var(--glass-border);">
                <button class="btn btn-ghost" onclick="navigateTo('cases')">Cancel</button>
                <button class="btn btn-primary btn-glow" onclick="submitNewCase()" id="btnCreateCase">
                    <span>Register & Analyze</span>
                </button>
            </div>
        </div>
    `;
    initGlassSpotlight();
}

function applyPreset(key) {
    const p = PRESET_TEMPLATES[key];
    if (!p) return;
    document.getElementById('caseTitle').value = p.title;
    document.getElementById('caseSymptom').value = p.symptom;
    document.getElementById('caseTopology').value = p.topology;
    document.getElementById('caseShowOutputs').value = p.show_outputs;
    document.getElementById('caseExpectedFault').value = p.expected_fault;
    document.getElementById('caseConcept').value = p.concept;
    document.getElementById('caseOsiLayer').value = p.osi_layer;
    document.getElementById('caseSeverity').value = p.severity;
    showToast(`Loaded ${p.concept} scenario preset`, 'info');
}

async function submitNewCase() {
    const title = document.getElementById('caseTitle').value.trim();
    const symptom = document.getElementById('caseSymptom').value.trim();

    if (!title || !symptom) {
        showToast('Please provide both Title and Symptom', 'error');
        return;
    }

    const btn = document.getElementById('btnCreateCase');
    btn.innerHTML = '<span>Saving Incident...</span>';
    btn.disabled = true;

    try {
        const data = {
            title: title,
            symptom: symptom,
            topology_notes: document.getElementById('caseTopology').value.trim(),
            show_outputs: document.getElementById('caseShowOutputs').value.trim(),
            expected_fault: document.getElementById('caseExpectedFault').value.trim(),
            concept: document.getElementById('caseConcept').value,
            osi_layer: document.getElementById('caseOsiLayer').value,
            severity: document.getElementById('caseSeverity').value || 'Medium'
        };

        const result = await api.createCase(data);
        showToast(`Incident ${result.case_id} registered`, 'success');
        navigateTo('case-detail', result.case_id);
    } catch (err) {
        showToast(`Failed to register incident: ${err.message}`, 'error');
    } finally {
        btn.innerHTML = '<span>Register & Analyze</span>';
        btn.disabled = false;
    }
}
