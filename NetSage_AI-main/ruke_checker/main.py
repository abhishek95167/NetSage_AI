"""
NetSage AI — Rule Checker Orchestrator
Runs all deterministic network checks and aggregates results.
"""

from typing import List, Dict
from rule_checker.ip_checks import check_duplicate_ips
from rule_checker.subnet_checks import check_subnet_masks
from rule_checker.gateway_checks import check_gateway_mismatch
from rule_checker.interface_checks import check_interface_down
from rule_checker.vlan_checks import check_missing_vlans
from rule_checker.routing_checks import check_missing_routes


def run_all_checks(show_output: str, topology_notes: str = "", symptom: str = "") -> List[Dict]:
    """
    Run all deterministic network validation checks on the provided output.
    Returns a list of check results.
    """
    combined_input = f"{show_output}\n{topology_notes}\n{symptom}"

    all_results = []

    # Run each check
    all_results.extend(check_duplicate_ips(combined_input))
    all_results.extend(check_subnet_masks(combined_input))
    all_results.extend(check_gateway_mismatch(combined_input))
    all_results.extend(check_interface_down(combined_input))
    all_results.extend(check_missing_vlans(combined_input))
    all_results.extend(check_missing_routes(combined_input))

    return all_results


def get_failures_only(results: List[Dict]) -> List[Dict]:
    """Filter results to only include failures."""
    return [r for r in results if r.get("status") == "FAIL"]


def get_summary(results: List[Dict]) -> Dict:
    """Get a summary of check results."""
    total = len(results)
    failures = len([r for r in results if r.get("status") == "FAIL"])
    passes = len([r for r in results if r.get("status") == "PASS"])

    severity_counts = {}
    for r in results:
        if r.get("status") == "FAIL":
            sev = r.get("severity", "UNKNOWN")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "total_checks": total,
        "passed": passes,
        "failed": failures,
        "severity_breakdown": severity_counts
    }


if __name__ == "__main__":
    # Example usage
    sample_output = """
    SW1#show ip interface brief
    Interface              IP-Address      OK? Method Status                Protocol
    FastEthernet0/1        unassigned      YES unset  up                    up
    FastEthernet0/5        unassigned      YES unset  administratively down down

    PC>ipconfig
       IPv4 Address....................: 10.10.10.50
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: 10.10.20.1
    """

    results = run_all_checks(sample_output)
    print("\n=== NetSage AI Rule Checker Results ===\n")
    for r in results:
        status_icon = "✓" if r["status"] == "PASS" else "✗"
        print(f"  [{status_icon}] {r['check']} — {r['status']} ({r['severity']})")
        print(f"      {r['message']}")
        if r["status"] == "FAIL":
            print(f"      Evidence: {r['evidence']}")
        print()

    summary = get_summary(results)
    print(f"\nSummary: {summary['passed']} passed, {summary['failed']} failed out of {summary['total_checks']} checks")
