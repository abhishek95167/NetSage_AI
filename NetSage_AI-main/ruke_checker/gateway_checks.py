"""
NetSage AI — Gateway Mismatch Checks
Detects when a host's default gateway is outside its subnet.
"""

import re
from typing import List, Dict


def ip_to_int(ip: str) -> int:
    """Convert IP address string to integer."""
    parts = ip.split('.')
    return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def mask_to_int(mask: str) -> int:
    """Convert subnet mask to integer."""
    return ip_to_int(mask)


def cidr_to_mask_int(cidr: int) -> int:
    """Convert CIDR prefix to mask integer."""
    if cidr == 0:
        return 0
    return (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF


def check_gateway_mismatch(show_output: str) -> List[Dict]:
    """
    Detect when a host's default gateway is not on the same subnet as the host.
    Parses ipconfig-style output for IP, mask, and gateway.
    """
    results = []

    # Parse ipconfig-style output
    ip_pattern = re.compile(
        r'IPv4 Address[.\s]*:\s*((?:\d{1,3}\.){3}\d{1,3})',
        re.IGNORECASE
    )
    mask_pattern = re.compile(
        r'Subnet Mask[.\s]*:\s*((?:\d{1,3}\.){3}\d{1,3})',
        re.IGNORECASE
    )
    gw_pattern = re.compile(
        r'Default Gateway[.\s]*:\s*((?:\d{1,3}\.){3}\d{1,3})',
        re.IGNORECASE
    )

    ip_matches = ip_pattern.findall(show_output)
    mask_matches = mask_pattern.findall(show_output)
    gw_matches = gw_pattern.findall(show_output)

    # Check each IP/mask/gateway combination
    for i in range(min(len(ip_matches), len(mask_matches), len(gw_matches))):
        host_ip = ip_matches[i]
        subnet_mask = mask_matches[i]
        gateway = gw_matches[i]

        if gateway in ('0.0.0.0', ''):
            continue

        host_int = ip_to_int(host_ip)
        mask_int = mask_to_int(subnet_mask)
        gw_int = ip_to_int(gateway)

        host_network = host_int & mask_int
        gw_network = gw_int & mask_int

        if host_network != gw_network:
            results.append({
                "check": "gateway_mismatch",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"Host IP: {host_ip}, Mask: {subnet_mask}, Gateway: {gateway}",
                "message": f"Default gateway {gateway} is outside the host subnet ({host_ip}/{subnet_mask}). The gateway must be on the same subnet as the host."
            })
        else:
            results.append({
                "check": "gateway_mismatch",
                "status": "PASS",
                "severity": "LOW",
                "evidence": f"Host IP: {host_ip}, Mask: {subnet_mask}, Gateway: {gateway}",
                "message": f"Default gateway {gateway} is correctly within the host subnet."
            })

    if not results:
        # Try to detect gateway in show command format
        gw_cmd_pattern = re.compile(
            r'default-router\s+((?:\d{1,3}\.){3}\d{1,3})',
            re.IGNORECASE
        )
        network_pattern = re.compile(
            r'network\s+((?:\d{1,3}\.){3}\d{1,3})\s+((?:\d{1,3}\.){3}\d{1,3})',
            re.IGNORECASE
        )

        gw_cmd_matches = gw_cmd_pattern.findall(show_output)
        net_matches = network_pattern.findall(show_output)

        for gw in gw_cmd_matches:
            for net_ip, net_mask in net_matches:
                gw_int = ip_to_int(gw)
                net_int = ip_to_int(net_ip)
                mask_int = mask_to_int(net_mask)

                if (gw_int & mask_int) != (net_int & mask_int):
                    results.append({
                        "check": "gateway_mismatch",
                        "status": "FAIL",
                        "severity": "HIGH",
                        "evidence": f"DHCP default-router: {gw}, Network: {net_ip} {net_mask}",
                        "message": f"DHCP default-router {gw} is not within the configured network {net_ip}/{net_mask}."
                    })

    if not results:
        results.append({
            "check": "gateway_mismatch",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "No gateway configuration found to check",
            "message": "No gateway mismatch detected (or insufficient data to check)."
        })

    return results
