"""
NetSage AI — VLAN Checks
Detects VLAN references that do not exist or VLAN misconfigurations.
"""

import re
from typing import List, Dict


def check_missing_vlans(show_output: str) -> List[Dict]:
    """
    Detect VLAN references that don't exist in the VLAN database.
    Checks access port VLAN assignments, trunk allowed VLANs, etc.
    """
    results = []

    # Extract VLANs from 'show vlan brief'
    vlan_db_pattern = re.compile(r'^(\d+)\s+\S+\s+active', re.MULTILINE | re.IGNORECASE)
    existing_vlans = set(int(v) for v in vlan_db_pattern.findall(show_output))

    # Always add VLAN 1 (default)
    if existing_vlans:
        existing_vlans.add(1)

    # Check access port VLAN assignments
    access_vlan_pattern = re.compile(
        r'Access Mode VLAN:\s*(\d+)',
        re.IGNORECASE
    )
    for match in access_vlan_pattern.findall(show_output):
        vlan_id = int(match)
        if existing_vlans and vlan_id not in existing_vlans:
            results.append({
                "check": "missing_vlan",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"Access port assigned to VLAN {vlan_id}, existing VLANs: {sorted(existing_vlans)}",
                "message": f"Access port is assigned to VLAN {vlan_id} which does not exist in the VLAN database. Port will be inactive."
            })

    # Check trunk allowed VLANs vs existing VLANs
    trunk_allowed_pattern = re.compile(
        r'Vlans allowed on trunk\s*\n\S+\s+([\d,\-]+)',
        re.IGNORECASE
    )
    trunk_matches = trunk_allowed_pattern.findall(show_output)
    for vlan_list_str in trunk_matches:
        trunk_vlans = _parse_vlan_list(vlan_list_str)
        if existing_vlans:
            missing = trunk_vlans - existing_vlans
            for v in missing:
                if v > 1 and v < 4095:
                    results.append({
                        "check": "missing_vlan",
                        "status": "FAIL",
                        "severity": "MEDIUM",
                        "evidence": f"VLAN {v} allowed on trunk but not in VLAN database",
                        "message": f"VLAN {v} is allowed on the trunk link but does not exist in the local VLAN database."
                    })

    # Check for Native VLAN mismatch
    native_pattern = re.compile(
        r'Native\s+(?:vlan|VLAN)\s*[:\s]\s*(\d+)',
        re.IGNORECASE
    )
    # Also match the trunk table format: "Fa0/24  on  802.1q  trunking  1"
    trunk_native_pattern = re.compile(
        r'^\s*\S+\s+\S+\s+\S+\s+trunking\s+(\d+)',
        re.IGNORECASE | re.MULTILINE
    )
    native_vlans = [int(v) for v in native_pattern.findall(show_output)]
    native_vlans.extend(int(v) for v in trunk_native_pattern.findall(show_output))
    if len(native_vlans) >= 2:
        unique_natives = set(native_vlans)
        if len(unique_natives) > 1:
            results.append({
                "check": "missing_vlan",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"Native VLAN values found: {sorted(unique_natives)}",
                "message": f"Native VLAN mismatch detected. Different ends of the trunk have different native VLANs: {sorted(unique_natives)}."
            })

    # Check for VTP domain mismatch
    vtp_domain_pattern = re.compile(
        r'VTP Domain Name\s*:\s*(\S+)',
        re.IGNORECASE
    )
    vtp_domains = vtp_domain_pattern.findall(show_output)
    if len(vtp_domains) >= 2:
        unique_domains = set(vtp_domains)
        if len(unique_domains) > 1:
            results.append({
                "check": "missing_vlan",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"VTP domains found: {list(unique_domains)}",
                "message": f"VTP domain name mismatch: {list(unique_domains)}. Switches must be in the same VTP domain to share VLAN information."
            })

    if not results:
        results.append({
            "check": "missing_vlan",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "No VLAN issues detected",
            "message": "All referenced VLANs exist and configurations appear consistent."
        })

    return results


def _parse_vlan_list(vlan_str: str) -> set:
    """Parse a VLAN list string like '1,10,20-30' into a set of VLAN IDs."""
    vlans = set()
    parts = vlan_str.strip().split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                for v in range(int(start), int(end) + 1):
                    vlans.add(v)
            except ValueError:
                pass
        else:
            try:
                vlans.add(int(part))
            except ValueError:
                pass
    return vlans
