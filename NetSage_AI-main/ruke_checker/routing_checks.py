"""
NetSage AI — Routing Checks
Detects missing routes and routing configuration issues.
"""

import re
from typing import List, Dict


def check_missing_routes(show_output: str) -> List[Dict]:
    """
    Detect when required routes are absent from the routing table.
    Checks for unreachable destinations, routing loops, and missing routes.
    """
    results = []

    # Detect "Destination host unreachable" — indicates missing route
    unreachable_pattern = re.compile(
        r'(?:Destination host unreachable|Destination net unreachable|'
        r'No route to host|network is unreachable)',
        re.IGNORECASE
    )
    if unreachable_pattern.search(show_output):
        results.append({
            "check": "missing_route",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": "Router reports 'Destination host unreachable' or similar",
            "message": "Missing route detected. The router has no route to the destination network."
        })

    # Detect routing loops via traceroute (same hops repeating)
    tracert_pattern = re.compile(
        r'(?:tracert|traceroute)',
        re.IGNORECASE
    )
    if tracert_pattern.search(show_output):
        hop_pattern = re.compile(r'\d+\s+((?:\d{1,3}\.){3}\d{1,3})')
        hops = hop_pattern.findall(show_output)
        if len(hops) >= 4:
            # Check for repeating pattern
            for i in range(len(hops) - 3):
                if hops[i] == hops[i + 2] and hops[i + 1] == hops[i + 3]:
                    results.append({
                        "check": "missing_route",
                        "status": "FAIL",
                        "severity": "CRITICAL",
                        "evidence": f"Routing loop detected between {hops[i]} and {hops[i+1]}",
                        "message": f"Routing loop detected. Packets are bouncing between {hops[i]} and {hops[i+1]}. Check static routes or routing protocol configuration on both routers."
                    })
                    break

    # Check for static routes pointing to each other (routing loop)
    static_route_pattern = re.compile(
        r'S\s+((?:\d{1,3}\.){3}\d{1,3})/\d+\s+\[[\d/]+\]\s+via\s+((?:\d{1,3}\.){3}\d{1,3})'
    )
    static_routes = static_route_pattern.findall(show_output)
    if len(static_routes) >= 2:
        # Check if two routes create a loop
        for i in range(len(static_routes)):
            for j in range(i + 1, len(static_routes)):
                dest1, nexthop1 = static_routes[i]
                dest2, nexthop2 = static_routes[j]
                # Simple loop detection: route to A via B, and route to same dest via different router
                if dest1 == dest2 and nexthop1 != nexthop2:
                    pass  # Might be ECMP, not necessarily a loop

    # Check for default route existence when needed
    ping_fail_pattern = re.compile(r'Success rate is 0 percent', re.IGNORECASE)
    has_default_route = bool(re.search(r'Gateway of last resort is \d', show_output))
    no_default = bool(re.search(r'Gateway of last resort is not set', show_output))

    if ping_fail_pattern.search(show_output) and no_default:
        results.append({
            "check": "missing_route",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": "Ping fails and 'Gateway of last resort is not set'",
            "message": "No default route configured and pings are failing. Consider adding a default route or specific static route."
        })

    # Check for OSPF/EIGRP neighbor issues
    ospf_no_neighbor = bool(re.search(r'show ip ospf neighbor\s*\n\s*\n', show_output, re.IGNORECASE))
    eigrp_no_neighbor = bool(re.search(r'show ip eigrp neighbors\s*\n\s*\n', show_output, re.IGNORECASE))

    if ospf_no_neighbor:
        results.append({
            "check": "missing_route",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": "show ip ospf neighbor returns empty — no OSPF adjacencies",
            "message": "No OSPF neighbors formed. Check area IDs, hello/dead timers, network statements, and authentication."
        })

    if eigrp_no_neighbor:
        results.append({
            "check": "missing_route",
            "status": "FAIL",
            "severity": "HIGH",
            "evidence": "show ip eigrp neighbors returns empty — no EIGRP adjacencies",
            "message": "No EIGRP neighbors formed. Check AS numbers, network statements, and interface configuration."
        })

    # Check for OSPF area mismatch
    ospf_area_pattern = re.compile(r'Area\s+(\d+)', re.IGNORECASE)
    areas = ospf_area_pattern.findall(show_output)
    if len(areas) >= 2:
        unique_areas = set(areas)
        if len(unique_areas) > 1:
            # Could be legitimate multi-area or could be mismatch
            # Only flag if it appears in interface context showing both sides
            area_lines = re.findall(r'Internet Address.*?Area\s+(\d+)', show_output, re.IGNORECASE | re.DOTALL)
            if len(area_lines) >= 2 and len(set(area_lines)) > 1:
                results.append({
                    "check": "missing_route",
                    "status": "FAIL",
                    "severity": "CRITICAL",
                    "evidence": f"OSPF area mismatch detected: areas {list(set(area_lines))}",
                    "message": "OSPF area mismatch between connected interfaces. Both sides of a link must be in the same OSPF area."
                })

    # Check for EIGRP AS mismatch
    eigrp_as_pattern = re.compile(r'router eigrp\s+(\d+)', re.IGNORECASE)
    eigrp_as_numbers = eigrp_as_pattern.findall(show_output)
    if len(eigrp_as_numbers) >= 2:
        unique_as = set(eigrp_as_numbers)
        if len(unique_as) > 1:
            results.append({
                "check": "missing_route",
                "status": "FAIL",
                "severity": "HIGH",
                "evidence": f"EIGRP AS numbers found: {list(unique_as)}",
                "message": f"EIGRP AS number mismatch: {list(unique_as)}. Both routers must use the same AS number to form a neighbor relationship."
            })

    if not results:
        results.append({
            "check": "missing_route",
            "status": "PASS",
            "severity": "LOW",
            "evidence": "No routing issues detected",
            "message": "No missing routes or routing problems detected."
        })

    return results
