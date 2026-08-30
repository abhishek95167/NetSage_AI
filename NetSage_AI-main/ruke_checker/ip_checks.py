"""
NetSage AI — IP Address Checks
Detects duplicate IP assignments from show command outputs.
"""

import re
from typing import List, Dict


def check_duplicate_ips(show_output: str) -> List[Dict]:
    """
    Detect duplicate IP addresses in show command output.
    Looks for IP addresses across multiple device outputs and flags duplicates.
    """
    results = []

    # Extract IP addresses with their context
    ip_pattern = re.compile(
        r'(?:IPv4 Address[.\s]*:|Internet address is |IP-Address\s+|'
        r'ip address\s+|address is\s+|Address\s*:\s*)'
        r'\s*((?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d))',
        re.IGNORECASE
    )

    # Also detect explicit duplicate address messages
    dup_pattern = re.compile(
        r'%IP-\d+-DUPADDR:\s*Duplicate address\s+([\d.]+)',
        re.IGNORECASE
    )

    # Find explicit duplicate warnings
    dup_matches = dup_pattern.findall(show_output)
    for dup_ip in dup_matches:
        results.append({
            "check": "duplicate_ip",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": f"System log reports duplicate address: {dup_ip}",
            "message": f"Duplicate IP address {dup_ip} detected. Multiple devices have the same IP, causing intermittent connectivity."
        })

    # Find all IP addresses and check for duplicates
    ip_addresses = {}
    lines = show_output.split('\n')
    for i, line in enumerate(lines):
        matches = ip_pattern.findall(line)
        for ip in matches:
            if ip in ('0.0.0.0', '255.255.255.255', '127.0.0.1'):
                continue
            if ip.startswith('169.254.'):
                continue
            if ip not in ip_addresses:
                ip_addresses[ip] = []
            ip_addresses[ip].append(line.strip())

    for ip, occurrences in ip_addresses.items():
        if len(occurrences) > 1:
            already_reported = any(ip in r.get("evidence", "") for r in results)
            if not already_reported:
                results.append({
                    "check": "duplicate_ip",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "evidence": f"IP {ip} found in multiple contexts: {'; '.join(occurrences[:3])}",
                    "message": f"Possible duplicate IP address {ip} detected across multiple interfaces or devices."
                })

    if not results:
        results.append({
            "check": "duplicate_ip",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "No duplicate IPs found in provided output",
            "message": "No duplicate IP addresses detected."
        })

    return results
