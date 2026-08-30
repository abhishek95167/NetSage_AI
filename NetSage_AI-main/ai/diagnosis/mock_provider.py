"""
NetSage AI — Mock AI Provider
Provides realistic, case-aware demo diagnoses without requiring an API key.
All responses are clearly labeled as demo data.
"""

import json
import re
from typing import Dict, Optional


# Case-specific mock diagnoses mapped by keywords in symptoms/faults
MOCK_DIAGNOSES = {
    "vlan_assignment": {
        "root_cause": "[DEMO MODE] PC is assigned to the wrong VLAN. The show vlan brief output confirms the port is listed under the incorrect VLAN, and the switchport configuration shows the access VLAN does not match the expected VLAN.",
        "confidence": 92,
        "osi_layer": "Layer 2",
        "evidence": [
            "Port is listed under the wrong VLAN in show vlan brief",
            "Access Mode VLAN in show interfaces switchport does not match expected VLAN"
        ],
        "next_command": "show mac address-table",
        "fix_steps": [
            "Enter interface configuration mode for the affected port",
            "Assign correct VLAN: switchport access vlan <correct_vlan>",
            "Verify with: show vlan brief",
            "Test connectivity from the affected PC"
        ],
        "alternative_causes": []
    },
    "trunk_vlan": {
        "root_cause": "[DEMO MODE] Required VLAN is not allowed on the trunk link. The show interfaces trunk output shows the trunk is only passing specific VLANs, and the required VLAN is excluded from the allowed list.",
        "confidence": 95,
        "osi_layer": "Layer 2",
        "evidence": [
            "show interfaces trunk shows limited VLANs in 'allowed on trunk' list",
            "Required VLAN is not listed in the trunk's allowed VLAN list"
        ],
        "next_command": "show interfaces trunk",
        "fix_steps": [
            "Enter interface configuration mode for the trunk port",
            "Add the missing VLAN: switchport trunk allowed vlan add <vlan_id>",
            "Verify with: show interfaces trunk",
            "Test cross-switch connectivity for the affected VLAN"
        ],
        "alternative_causes": []
    },
    "gateway_wrong": {
        "root_cause": "[DEMO MODE] The default gateway configured on the PC is not within its subnet. The ipconfig output shows the gateway IP belongs to a different subnet than the PC's assigned address.",
        "confidence": 90,
        "osi_layer": "Layer 3",
        "evidence": [
            "PC IP address and subnet mask define a specific network",
            "Default gateway IP does not fall within the PC's subnet",
            "Ping to gateway succeeds (ARP resolves locally) but remote traffic fails"
        ],
        "next_command": "show ip interface brief",
        "fix_steps": [
            "Correct the default gateway on the PC to match the router's interface IP on the same subnet",
            "Verify connectivity with ping to the correct gateway",
            "Test end-to-end connectivity"
        ],
        "alternative_causes": [
            "Router interface might have incorrect IP"
        ]
    },
    "dhcp_pool": {
        "root_cause": "[DEMO MODE] DHCP pool is configured with the wrong network address or has all addresses excluded. The pool network does not match the connected interface subnet, preventing address assignment.",
        "confidence": 93,
        "osi_layer": "Layer 7",
        "evidence": [
            "DHCP pool network does not match the interface IP subnet",
            "No DHCP bindings exist despite pool being configured",
            "Interface is up and correctly addressed"
        ],
        "next_command": "show ip dhcp binding",
        "fix_steps": [
            "Remove incorrect DHCP pool: no ip dhcp pool <name>",
            "Create new pool with correct network: ip dhcp pool <name>",
            "Configure correct network statement: network <correct_subnet> <mask>",
            "Set correct default-router and dns-server",
            "Verify with: show ip dhcp pool"
        ],
        "alternative_causes": [
            "DHCP excluded-address range may cover all addresses",
            "ip helper-address may be missing on relay interface"
        ]
    },
    "dns": {
        "root_cause": "[DEMO MODE] DNS server is either not configured in the DHCP pool, unreachable from the client network, or there is no route to the DNS server's network.",
        "confidence": 85,
        "osi_layer": "Layer 7",
        "evidence": [
            "DNS Servers field shows 0.0.0.0 or is empty in ipconfig",
            "Direct IP connectivity works but hostname resolution fails"
        ],
        "next_command": "show running-config | section dhcp",
        "fix_steps": [
            "Add DNS server to DHCP pool: dns-server <dns_ip>",
            "Verify route to DNS server exists: show ip route",
            "Release and renew DHCP on clients: ipconfig /release then ipconfig /renew",
            "Test with: nslookup or ping by hostname"
        ],
        "alternative_causes": [
            "DNS server may be down",
            "ACL may be blocking DNS traffic (UDP port 53)",
            "Route to DNS server subnet may be missing"
        ]
    },
    "static_route": {
        "root_cause": "[DEMO MODE] Missing static route or incorrect next-hop address. The routing table does not contain a route to the destination network, causing the router to drop packets.",
        "confidence": 88,
        "osi_layer": "Layer 3",
        "evidence": [
            "show ip route does not contain a route to the destination network",
            "Gateway of last resort is not set",
            "Ping to destination shows 0% success rate"
        ],
        "next_command": "show ip route",
        "fix_steps": [
            "Add static route: ip route <dest_network> <mask> <next_hop>",
            "Or configure default route: ip route 0.0.0.0 0.0.0.0 <next_hop>",
            "Verify with: show ip route",
            "Test with: ping <destination>"
        ],
        "alternative_causes": [
            "Next-hop router may also be missing a return route",
            "Routing protocol may not be advertising the network"
        ]
    },
    "ospf": {
        "root_cause": "[DEMO MODE] OSPF neighbor relationship not forming due to area mismatch, authentication mismatch, or hello/dead timer mismatch between the connected interfaces.",
        "confidence": 87,
        "osi_layer": "Layer 3",
        "evidence": [
            "show ip ospf neighbor returns empty — no adjacencies",
            "OSPF interfaces are up but area IDs differ between routers"
        ],
        "next_command": "show ip ospf interface",
        "fix_steps": [
            "Verify both interfaces are in the same OSPF area",
            "Check hello/dead timers match: show ip ospf interface",
            "Verify network statements include the correct interfaces",
            "Check authentication settings match on both sides",
            "Verify with: show ip ospf neighbor"
        ],
        "alternative_causes": [
            "MTU mismatch can prevent OSPF adjacency in some cases",
            "Network type mismatch (broadcast vs point-to-point)"
        ]
    },
    "eigrp": {
        "root_cause": "[DEMO MODE] EIGRP autonomous system (AS) number mismatch between routers. Both routers must use the same AS number to form a neighbor relationship.",
        "confidence": 92,
        "osi_layer": "Layer 3",
        "evidence": [
            "show ip eigrp neighbors returns empty",
            "Running configuration shows different AS numbers on each router"
        ],
        "next_command": "show ip eigrp neighbors",
        "fix_steps": [
            "Correct the EIGRP AS number on one of the routers to match the other",
            "Ensure network statements cover the connected interfaces",
            "Verify with: show ip eigrp neighbors",
            "Check route propagation: show ip route eigrp"
        ],
        "alternative_causes": []
    },
    "acl_block": {
        "root_cause": "[DEMO MODE] An access control list (ACL) is blocking legitimate traffic. The ACL contains an explicit or implicit deny rule that matches the traffic being blocked.",
        "confidence": 90,
        "osi_layer": "Layer 4",
        "evidence": [
            "show access-lists shows deny rule matching the blocked traffic",
            "Match count on the deny rule is incrementing",
            "Other traffic types are permitted"
        ],
        "next_command": "show access-lists",
        "fix_steps": [
            "Identify the specific ACL rule blocking traffic",
            "Add a permit rule before the deny: permit tcp <source> <dest> eq <port>",
            "Or remove the inappropriate deny rule",
            "Verify with: show access-lists",
            "Test the previously blocked traffic"
        ],
        "alternative_causes": [
            "Implicit deny at end of ACL blocking all unmatched traffic"
        ]
    },
    "nat": {
        "root_cause": "[DEMO MODE] NAT is misconfigured. Either the inside/outside interfaces are not designated, the NAT pool is exhausted, or the static mapping uses incorrect port numbers.",
        "confidence": 85,
        "osi_layer": "Layer 3",
        "evidence": [
            "show ip nat translations shows no translations or incorrect mappings",
            "show ip nat statistics shows missing inside/outside interfaces or pool exhaustion"
        ],
        "next_command": "show ip nat statistics",
        "fix_steps": [
            "Verify inside/outside interface designations: ip nat inside / ip nat outside",
            "Check NAT pool or overload configuration",
            "Verify ACL matches internal hosts",
            "Clear NAT translations: clear ip nat translation *",
            "Verify with: show ip nat translations"
        ],
        "alternative_causes": [
            "ACL used for NAT may not match the correct source addresses",
            "NAT pool addresses may conflict with other addressing"
        ]
    },
    "interface_down": {
        "root_cause": "[DEMO MODE] Interface is administratively shutdown or in err-disabled state. The interface must be manually enabled before traffic can pass.",
        "confidence": 95,
        "osi_layer": "Layer 1",
        "evidence": [
            "show ip interface brief shows interface status as 'administratively down'",
            "show interfaces confirms the interface is disabled"
        ],
        "next_command": "show interfaces",
        "fix_steps": [
            "Enter interface configuration: interface <interface_id>",
            "Enable the interface: no shutdown",
            "If err-disabled, first resolve the root cause then: shutdown followed by no shutdown",
            "Verify with: show ip interface brief"
        ],
        "alternative_causes": [
            "Port security violation may have caused err-disabled state",
            "Physical cable issue"
        ]
    },
    "wireless": {
        "root_cause": "[DEMO MODE] Wireless network issue detected. This could be a disabled SSID, security type mismatch, missing guest isolation ACL, or channel overlap causing interference.",
        "confidence": 80,
        "osi_layer": "Layer 2",
        "evidence": [
            "Wireless LAN configuration shows potential misconfiguration",
            "Client unable to connect or has unexpected network access"
        ],
        "next_command": "show wlan summary",
        "fix_steps": [
            "Verify WLAN status is Enabled: show wlan <id>",
            "Check security settings match client configuration",
            "If guest isolation issue: apply ACL to guest VLAN interface",
            "Verify with: show wlan summary"
        ],
        "alternative_causes": [
            "AP may need to be rebooted",
            "Channel interference from adjacent APs",
            "Client driver or configuration issue"
        ]
    },
    "guest_isolation": {
        "root_cause": "[DEMO MODE] Guest wireless network is not properly isolated from internal resources. No ACL is applied to the guest VLAN interface, allowing guest users to access internal servers and resources. This is a security violation.",
        "confidence": 88,
        "osi_layer": "Layer 4",
        "evidence": [
            "Guest PC can successfully ping internal server",
            "No ACL applied on the guest VLAN subinterface",
            "show access-lists shows empty or no ACL for guest traffic"
        ],
        "next_command": "show ip interface",
        "fix_steps": [
            "Create an extended ACL to deny guest-to-internal traffic: access-list 150 deny ip <guest_subnet> <wildcard> <internal_subnet> <wildcard>",
            "Permit guest internet access: access-list 150 permit ip <guest_subnet> <wildcard> any",
            "Apply ACL inbound on guest VLAN interface: ip access-group 150 in",
            "Verify guest cannot reach internal servers",
            "Verify guest can still reach the internet"
        ],
        "alternative_causes": [
            "Guest VLAN may be incorrectly mapped to the management interface",
            "Inter-VLAN routing may need additional restrictions"
        ]
    },
    "duplex": {
        "root_cause": "[DEMO MODE] Duplex mismatch detected between connected interfaces. One end is configured for full-duplex while the other is half-duplex, causing CRC errors, late collisions, and severely degraded performance.",
        "confidence": 91,
        "osi_layer": "Layer 1",
        "evidence": [
            "One interface shows full-duplex and the other shows half-duplex",
            "High CRC error count on the half-duplex interface",
            "Late collisions indicating duplex mismatch"
        ],
        "next_command": "show interfaces",
        "fix_steps": [
            "Set both interfaces to the same duplex mode (preferably full-duplex)",
            "interface <port>: duplex full",
            "Verify with: show interfaces <port>",
            "Monitor for reduction in CRC errors"
        ],
        "alternative_causes": [
            "Cable quality issue",
            "Auto-negotiation failure"
        ]
    },
    "routing_loop": {
        "root_cause": "[DEMO MODE] Routing loop detected. Two routers have static routes pointing to each other for the same destination, causing packets to bounce indefinitely until TTL expires.",
        "confidence": 94,
        "osi_layer": "Layer 3",
        "evidence": [
            "Traceroute shows repeating hops between two router IPs",
            "Static routes on both routers point to each other for the destination",
            "TTL exceeded messages from both routers"
        ],
        "next_command": "show ip route",
        "fix_steps": [
            "Identify the correct path to the destination network",
            "Correct the static route on the router with the wrong next-hop",
            "ip route <dest_network> <mask> <correct_next_hop>",
            "Verify with traceroute from the source",
            "Confirm no more looping behavior"
        ],
        "alternative_causes": []
    },
    "default": {
        "root_cause": "[DEMO MODE] Based on the provided symptoms and evidence, the issue appears to be a network configuration problem. Further analysis of specific show command outputs is needed to determine the exact root cause.",
        "confidence": 55,
        "osi_layer": "Layer 3",
        "evidence": [
            "Symptom indicates a connectivity or reachability problem",
            "Additional show command output needed for definitive diagnosis"
        ],
        "next_command": "show ip interface brief",
        "fix_steps": [
            "Gather additional diagnostic information using the recommended next command",
            "Review the output for interface status, IP addressing, and routing",
            "Identify the specific layer where the failure occurs",
            "Apply targeted fix based on findings"
        ],
        "alternative_causes": [
            "Physical connectivity issue (Layer 1)",
            "VLAN or switching issue (Layer 2)",
            "Routing or addressing issue (Layer 3)",
            "ACL or firewall issue (Layer 4)",
            "Application or service issue (Layer 7)"
        ]
    }
}


def _classify_case(symptom: str, show_output: str, topology: str, expected_fault: str = "") -> str:
    """Classify a case to select the most appropriate mock diagnosis."""
    combined = f"{symptom} {show_output} {topology} {expected_fault}".lower()

    # Check for specific patterns
    if any(kw in combined for kw in ["routing loop", "bouncing", "tracert", "traceroute", "loop"]):
        if "bounce" in combined or "loop" in combined:
            return "routing_loop"

    if any(kw in combined for kw in ["guest", "isolation", "guest wifi", "guest wireless", "security violation"]):
        return "guest_isolation"

    if any(kw in combined for kw in ["duplex", "crc", "late collision", "half-duplex"]):
        return "duplex"

    if "vlan" in combined and any(kw in combined for kw in ["wrong vlan", "assigned to", "access mode vlan"]):
        return "vlan_assignment"

    if "trunk" in combined and any(kw in combined for kw in ["not allow", "allowed on trunk", "vlan not"]):
        return "trunk_vlan"

    if any(kw in combined for kw in ["default gateway", "gateway", "wrong gateway"]) and "nat" not in combined:
        if "dhcp" not in combined or "gateway" in symptom.lower():
            return "gateway_wrong"

    if any(kw in combined for kw in ["dhcp", "ip address", "leased", "pool", "excluded", "helper"]):
        return "dhcp_pool"

    if any(kw in combined for kw in ["dns", "name resolution", "hostname", "nslookup"]):
        return "dns"

    if any(kw in combined for kw in ["ospf", "area mismatch"]):
        return "ospf"

    if any(kw in combined for kw in ["eigrp", "as number"]):
        return "eigrp"

    if any(kw in combined for kw in ["static route", "missing route", "no route", "default route", "ip route"]):
        return "static_route"

    if any(kw in combined for kw in ["acl", "access-list", "access list", "blocking", "deny"]):
        return "acl_block"

    if any(kw in combined for kw in ["nat", "translation", "inside source", "overload"]):
        return "nat"

    if any(kw in combined for kw in ["administratively down", "shutdown", "err-disabled", "interface down"]):
        return "interface_down"

    if any(kw in combined for kw in ["wireless", "wifi", "wlan", "ssid", "ap", "wpa"]):
        return "wireless"

    if any(kw in combined for kw in ["vlan", "native vlan", "vtp", "spanning-tree"]):
        return "vlan_assignment"

    if any(kw in combined for kw in ["routing", "route", "ospf", "eigrp", "bgp"]):
        return "static_route"

    return "default"


async def get_mock_diagnosis(symptom: str, topology_notes: str, show_outputs: str, expected_fault: str = "") -> Dict:
    """
    Generate a mock diagnosis based on case classification.
    Returns a realistic but clearly labeled demo response.
    """
    category = _classify_case(symptom, show_outputs, topology_notes, expected_fault)
    diagnosis = MOCK_DIAGNOSES.get(category, MOCK_DIAGNOSES["default"]).copy()

    # Deep copy lists
    diagnosis["evidence"] = list(diagnosis["evidence"])
    diagnosis["fix_steps"] = list(diagnosis["fix_steps"])
    diagnosis["alternative_causes"] = list(diagnosis["alternative_causes"])

    return diagnosis
