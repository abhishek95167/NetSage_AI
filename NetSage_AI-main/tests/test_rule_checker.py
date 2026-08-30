"""
NetSage AI — Rule Checker Tests
Tests for all deterministic network validation checks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rule_checker.ip_checks import check_duplicate_ips
from rule_checker.subnet_checks import check_subnet_masks
from rule_checker.gateway_checks import check_gateway_mismatch
from rule_checker.interface_checks import check_interface_down
from rule_checker.vlan_checks import check_missing_vlans
from rule_checker.routing_checks import check_missing_routes


def test_duplicate_ip_detection():
    """Test: Detect duplicate IP address from system log."""
    output = """
    PC-A>ipconfig
       IPv4 Address....................: 10.10.10.50
       Subnet Mask.....................: 255.255.255.0

    PC-B>ipconfig
       IPv4 Address....................: 10.10.10.50
       Subnet Mask.....................: 255.255.255.0

    %IP-4-DUPADDR: Duplicate address 10.10.10.50 on Vlan10
    """
    results = check_duplicate_ips(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected at least 1 duplicate IP failure, got {len(failures)}"
    assert any("10.10.10.50" in r["evidence"] or "10.10.10.50" in r["message"] for r in failures), \
        "Expected duplicate IP 10.10.10.50 in failure evidence"
    print("✓ test_duplicate_ip_detection passed")


def test_no_duplicate_ip():
    """Test: No duplicates should pass."""
    output = """
    PC>ipconfig
       IPv4 Address....................: 10.10.10.50
       Subnet Mask.....................: 255.255.255.0
    """
    results = check_duplicate_ips(output)
    passes = [r for r in results if r["status"] == "PASS"]
    assert len(passes) >= 1, "Expected PASS when no duplicates"
    print("✓ test_no_duplicate_ip passed")


def test_wrong_subnet_mask():
    """Test: Detect subnet mask mismatch between interfaces."""
    output = """
    R1#show interfaces gig0/1
    GigabitEthernet0/1 is up, line protocol is up
      Internet address is 10.0.0.1/24

    R2#show interfaces gig0/1
    GigabitEthernet0/1 is up, line protocol is up
      Internet address is 10.0.0.2/30
    """
    results = check_subnet_masks(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected subnet mask mismatch failure, got {len(failures)}"
    print("✓ test_wrong_subnet_mask passed")


def test_gateway_mismatch():
    """Test: Detect gateway outside host subnet."""
    output = """
    PC>ipconfig
       IPv4 Address....................: 10.10.10.10
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: 10.10.20.1
    """
    results = check_gateway_mismatch(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected gateway mismatch failure, got {len(failures)}"
    assert any("10.10.20.1" in r["evidence"] for r in failures), \
        "Expected gateway 10.10.20.1 in failure evidence"
    print("✓ test_gateway_mismatch passed")


def test_gateway_correct():
    """Test: Correct gateway should pass."""
    output = """
    PC>ipconfig
       IPv4 Address....................: 10.10.10.10
       Subnet Mask.....................: 255.255.255.0
       Default Gateway.................: 10.10.10.1
    """
    results = check_gateway_mismatch(output)
    passes = [r for r in results if r["status"] == "PASS"]
    assert len(passes) >= 1, "Expected PASS for correct gateway"
    print("✓ test_gateway_correct passed")


def test_interface_down():
    """Test: Detect administratively down interface."""
    output = """
    SW1#show ip interface brief
    Interface              IP-Address      OK? Method Status                Protocol
    FastEthernet0/1        unassigned      YES unset  up                    up
    FastEthernet0/5        unassigned      YES unset  administratively down down
    FastEthernet0/6        unassigned      YES unset  up                    up
    """
    results = check_interface_down(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected interface down failure, got {len(failures)}"
    assert any("Fa" in r["evidence"] or "FastEthernet0/5" in r["evidence"] for r in failures), \
        "Expected FastEthernet0/5 in failure evidence"
    print("✓ test_interface_down passed")


def test_all_interfaces_up():
    """Test: All up interfaces should pass."""
    output = """
    SW1#show ip interface brief
    Interface              IP-Address      OK? Method Status                Protocol
    FastEthernet0/1        unassigned      YES unset  up                    up
    FastEthernet0/2        unassigned      YES unset  up                    up
    """
    results = check_interface_down(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) == 0, f"Expected no interface down failures, got {len(failures)}"
    print("✓ test_all_interfaces_up passed")


def test_missing_vlan():
    """Test: Detect native VLAN mismatch."""
    output = """
    SW1#show interfaces trunk
    Port        Mode             Encapsulation  Status        Native vlan
    Fa0/24      on               802.1q         trunking      1

    SW2#show interfaces trunk
    Port        Mode             Encapsulation  Status        Native vlan
    Fa0/24      on               802.1q         trunking      99
    """
    results = check_missing_vlans(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected native VLAN mismatch, got {len(failures)}"
    print("✓ test_missing_vlan passed")


def test_missing_route():
    """Test: Detect missing route via unreachable message."""
    output = """
    R1#show ip route
    Gateway of last resort is not set
         10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
    C       10.0.0.0/30 is directly connected, Serial0/0/0
    C       10.10.10.0/24 is directly connected, GigabitEthernet0/0

    R1#ping 172.16.0.1
    Destination host unreachable.
    """
    results = check_missing_routes(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected missing route failure, got {len(failures)}"
    print("✓ test_missing_route passed")


def test_ospf_no_neighbor():
    """Test: Detect empty OSPF neighbor table."""
    output = """
    R1#show ip ospf neighbor

    R1#show ip ospf interface gig0/1
    Internet Address 10.0.0.1/30, Area 0
    """
    results = check_missing_routes(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected OSPF no neighbor failure, got {len(failures)}"
    print("✓ test_ospf_no_neighbor passed")


def test_eigrp_as_mismatch():
    """Test: Detect EIGRP AS number mismatch."""
    output = """
    R1#show running-config | section eigrp
    router eigrp 100
     network 10.0.0.0

    R2#show running-config | section eigrp
    router eigrp 200
     network 10.0.0.0
    """
    results = check_missing_routes(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected EIGRP AS mismatch failure, got {len(failures)}"
    print("✓ test_eigrp_as_mismatch passed")


def test_routing_loop():
    """Test: Detect routing loop in traceroute."""
    output = """
    PC>tracert 172.16.1.1
      1   10.10.10.1    1 ms
      2   10.0.0.2      2 ms
      3   10.0.0.1      3 ms
      4   10.0.0.2      4 ms
      5   10.0.0.1      5 ms
      6   10.0.0.2      6 ms
    """
    results = check_missing_routes(output)
    failures = [r for r in results if r["status"] == "FAIL"]
    assert len(failures) >= 1, f"Expected routing loop failure, got {len(failures)}"
    assert any("loop" in r["message"].lower() or "loop" in r["evidence"].lower() for r in failures), \
        "Expected 'loop' in failure message"
    print("✓ test_routing_loop passed")


if __name__ == "__main__":
    tests = [
        test_duplicate_ip_detection,
        test_no_duplicate_ip,
        test_wrong_subnet_mask,
        test_gateway_mismatch,
        test_gateway_correct,
        test_interface_down,
        test_all_interfaces_up,
        test_missing_vlan,
        test_missing_route,
        test_ospf_no_neighbor,
        test_eigrp_as_mismatch,
        test_routing_loop,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'='*50}")
