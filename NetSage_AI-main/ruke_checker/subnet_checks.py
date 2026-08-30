"""
NetSage AI — Subnet Mask Checks
Detects invalid or inconsistent subnet masks.
"""

import re
from typing import List, Dict


VALID_MASKS = {
    '0.0.0.0', '128.0.0.0', '192.0.0.0', '224.0.0.0', '240.0.0.0',
    '248.0.0.0', '252.0.0.0', '254.0.0.0', '255.0.0.0',
    '255.128.0.0', '255.192.0.0', '255.224.0.0', '255.240.0.0',
    '255.248.0.0', '255.252.0.0', '255.254.0.0', '255.255.0.0',
    '255.255.128.0', '255.255.192.0', '255.255.224.0', '255.255.240.0',
    '255.255.248.0', '255.255.252.0', '255.255.254.0', '255.255.255.0',
    '255.255.255.128', '255.255.255.192', '255.255.255.224', '255.255.255.240',
    '255.255.255.248', '255.255.255.252', '255.255.255.254', '255.255.255.255'
}

CIDR_TO_MASK = {
    0: '0.0.0.0', 1: '128.0.0.0', 2: '192.0.0.0', 3: '224.0.0.0',
    4: '240.0.0.0', 5: '248.0.0.0', 6: '252.0.0.0', 7: '254.0.0.0',
    8: '255.0.0.0', 9: '255.128.0.0', 10: '255.192.0.0', 11: '255.224.0.0',
    12: '255.240.0.0', 13: '255.248.0.0', 14: '255.252.0.0', 15: '255.254.0.0',
    16: '255.255.0.0', 17: '255.255.128.0', 18: '255.255.192.0',
    19: '255.255.224.0', 20: '255.255.240.0', 21: '255.255.248.0',
    22: '255.255.252.0', 23: '255.255.254.0', 24: '255.255.255.0',
    25: '255.255.255.128', 26: '255.255.255.192', 27: '255.255.255.224',
    28: '255.255.255.240', 29: '255.255.255.248', 30: '255.255.255.252',
    31: '255.255.255.254', 32: '255.255.255.255'
}


def ip_to_int(ip: str) -> int:
    """Convert IP address string to integer."""
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def mask_to_cidr(mask: str) -> int:
    """Convert subnet mask to CIDR notation."""
    for cidr, m in CIDR_TO_MASK.items():
        if m == mask:
            return cidr
    return -1


def check_subnet_masks(show_output: str) -> List[Dict]:
    """
    Detect invalid or inconsistent subnet masks in show command output.
    """
    results = []

    # Find subnet masks in ipconfig output
    mask_pattern = re.compile(
        r'Subnet Mask[.\s]*:\s*((?:\d{1,3}\.){3}\d{1,3})',
        re.IGNORECASE
    )

    # Find CIDR notation in interface output
    cidr_pattern = re.compile(
        r'((?:\d{1,3}\.){3}\d{1,3})/(\d{1,2})'
    )

    # Check dotted-decimal masks
    mask_matches = mask_pattern.findall(show_output)
    for mask in mask_matches:
        if mask not in VALID_MASKS:
            results.append({
                "check": "wrong_subnet_mask",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"Subnet Mask: {mask}",
                "message": f"Invalid subnet mask {mask} detected. This is not a valid contiguous subnet mask."
            })

    # Check CIDR notation for valid ranges and look for mismatches
    cidr_entries = []
    cidr_matches = cidr_pattern.findall(show_output)
    for ip, cidr in cidr_matches:
        cidr_int = int(cidr)
        if cidr_int < 0 or cidr_int > 32:
            results.append({
                "check": "wrong_subnet_mask",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"Interface {ip}/{cidr}",
                "message": f"Invalid CIDR prefix length /{cidr} detected. Must be between 0 and 32."
            })
        else:
            cidr_entries.append((ip, cidr_int))

    # Check for subnet mask mismatches on same link
    # Group IPs by network proximity
    if len(cidr_entries) >= 2:
        for i in range(len(cidr_entries)):
            for j in range(i + 1, len(cidr_entries)):
                ip1, cidr1 = cidr_entries[i]
                ip2, cidr2 = cidr_entries[j]
                # Check if IPs are on the same link (similar addresses)
                ip1_int = ip_to_int(ip1)
                ip2_int = ip_to_int(ip2)
                # Use the larger mask to check if they should be on the same subnet
                min_cidr = min(cidr1, cidr2)
                mask_int = (0xFFFFFFFF << (32 - min_cidr)) & 0xFFFFFFFF
                if (ip1_int & mask_int) == (ip2_int & mask_int) and cidr1 != cidr2:
                    results.append({
                        "check": "wrong_subnet_mask",
                        "status": "FAIL",
                        "severity": "MEDIUM",
                        "evidence": f"{ip1}/{cidr1} vs {ip2}/{cidr2}",
                        "message": f"Subnet mask mismatch detected: {ip1}/{cidr1} and {ip2}/{cidr2} appear to be on the same link but have different prefix lengths."
                    })

    if not results:
        results.append({
            "check": "wrong_subnet_mask",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "All subnet masks appear valid",
            "message": "No subnet mask issues detected."
        })

    return results
