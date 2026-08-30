"""
NetSage AI — AI-Human Agreement Rate Tests
Tests the agreement rate calculation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def calculate_agreement_rate(accepted: int, edited: int, rejected: int) -> float:
    """Calculate AI-Human agreement rate."""
    total_reviewed = accepted + edited + rejected
    if total_reviewed == 0:
        return 0.0
    return (accepted / total_reviewed) * 100


def test_all_accepted():
    """Test: 100% agreement when all accepted."""
    rate = calculate_agreement_rate(10, 0, 0)
    assert rate == 100.0, f"Expected 100.0, got {rate}"
    print("✓ test_all_accepted passed")


def test_all_rejected():
    """Test: 0% agreement when all rejected."""
    rate = calculate_agreement_rate(0, 0, 10)
    assert rate == 0.0, f"Expected 0.0, got {rate}"
    print("✓ test_all_rejected passed")


def test_mixed_reviews():
    """Test: Correct calculation for mixed reviews."""
    # 6 accepted, 2 edited, 2 rejected = 6/10 = 60%
    rate = calculate_agreement_rate(6, 2, 2)
    assert rate == 60.0, f"Expected 60.0, got {rate}"
    print("✓ test_mixed_reviews passed")


def test_no_reviews():
    """Test: 0% when no reviews."""
    rate = calculate_agreement_rate(0, 0, 0)
    assert rate == 0.0, f"Expected 0.0, got {rate}"
    print("✓ test_no_reviews passed")


def test_demo_data_rate():
    """Test: Agreement rate from seeded demo data (6 accepted, 2 edited, 2 rejected)."""
    # From seed.py: 6 accepted, 2 edited, 2 rejected
    rate = calculate_agreement_rate(6, 2, 2)
    assert 55.0 <= rate <= 65.0, f"Expected ~60%, got {rate}%"
    print("✓ test_demo_data_rate passed")


def test_precision():
    """Test: Rate handles fractional results correctly."""
    # 1 accepted, 2 edited = 1/3 = 33.33...%
    rate = calculate_agreement_rate(1, 2, 0)
    assert abs(rate - 33.333) < 0.1, f"Expected ~33.33, got {rate}"
    print("✓ test_precision passed")


if __name__ == "__main__":
    tests = [
        test_all_accepted,
        test_all_rejected,
        test_mixed_reviews,
        test_no_reviews,
        test_demo_data_rate,
        test_precision,
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
