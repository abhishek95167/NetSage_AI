"""
NetSage AI — Interface Down Checks
Detects interfaces that are administratively or operationally down.
"""

import re
from typing import List, Dict


def check_interface_down(show_output: str) -> List[Dict]:
    """
    Detect interfaces that are administratively or operationally down.
    Parses 'show ip interface brief' and 'show interfaces' output.
    """
    results = []

    # Pattern for 'show ip interface brief' output
    # Interface  IP-Address  OK?  Method  Status  Protocol
    brief_pattern = re.compile(
        r'((?:FastEthernet|GigabitEthernet|Serial|Vlan|Loopback|Tunnel|Port-channel)\S*)'
        r'\s+(\S+)\s+\S+\s+\S+\s+'
        r'(administratively down|down|up)\s+'
        r'(down|up)',
        re.IGNORECASE
    )

    # Pattern for 'show interfaces' output
    intf_status_pattern = re.compile(
        r'((?:FastEthernet|GigabitEthernet|Serial|Vlan|Loopback|Tunnel|Port-channel)\S*)'
        r'\s+is\s+(administratively down|down|up)',
        re.IGNORECASE
    )

    # Check 'show ip interface brief' style
    brief_matches = brief_pattern.findall(show_output)
    seen_interfaces = set()

    for intf, ip, status, protocol in brief_matches:
        intf_lower = intf.lower()
        if intf_lower in seen_interfaces:
            continue
        seen_interfaces.add(intf_lower)

        if 'administratively down' in status.lower():
            results.append({
                "check": "interface_down",
                "status": "FAIL",
                "severity": "MEDIUM",
                "evidence": f"{intf}: Status={status}, Protocol={protocol}",
                "message": f"Interface {intf} is administratively shutdown. Use 'no shutdown' to enable it."
            })
        elif status.lower() == 'down':
            results.append({
                "check": "interface_down",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"{intf}: Status={status}, Protocol={protocol}",
                "message": f"Interface {intf} is operationally down. Check physical connectivity and remote end."
            })
        elif protocol.lower() == 'down':
            results.append({
                "check": "interface_down",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"{intf}: Status={status}, Protocol={protocol}",
                "message": f"Interface {intf} line protocol is down. Layer 2 issue — check encapsulation, keepalives, or clock rate."
            })

    # Check 'show interfaces' style if no brief matches
    if not brief_matches:
        status_matches = intf_status_pattern.findall(show_output)
        for intf, status in status_matches:
            intf_lower = intf.lower()
            if intf_lower in seen_interfaces:
                continue
            seen_interfaces.add(intf_lower)

            if 'administratively down' in status.lower():
                results.append({
                    "check": "interface_down",
                    "status": "FAIL",
                    "severity": "MEDIUM",
                    "evidence": f"{intf} is {status}",
                    "message": f"Interface {intf} is administratively shutdown. Use 'no shutdown' to enable it."
                })
            elif 'down' in status.lower():
                results.append({
                    "check": "interface_down",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "evidence": f"{intf} is {status}",
                    "message": f"Interface {intf} is down. Check physical connectivity."
                })

    # Check for err-disabled
    errdisabled_pattern = re.compile(
        r'((?:FastEthernet|GigabitEthernet|Serial)\S*)\s+is\s+down.*?err-disabled',
        re.IGNORECASE
    )
    for match in errdisabled_pattern.findall(show_output):
        results.append({
            "check": "interface_down",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": f"{match} is err-disabled",
            "message": f"Interface {match} is in err-disabled state. Likely caused by port security violation, BPDU guard, or other security feature."
        })

    if not results:
        results.append({
            "check": "interface_down",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "All detected interfaces are up",
            "message": "No down interfaces detected."
        })

    return results
