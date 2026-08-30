"""
NetSage AI — AI Schema Validation Tests
Tests that AI diagnosis output matches the required JSON schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai.schemas.diagnosis_schema import validate_diagnosis


def test_valid_diagnosis():
    """Test: Valid diagnosis passes schema validation."""
    diagnosis = {
        "root_cause": "VLAN assignment error",
        "confidence": 92,
        "osi_layer": "Layer 2",
        "evidence": ["Port Fa0/1 is in VLAN 20", "Expected VLAN 10"],
        "next_command": "show vlan brief",
        "fix_steps": ["switchport access vlan 10", "verify with show vlan"],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert is_valid, f"Expected valid diagnosis, got errors: {errors}"
    assert len(errors) == 0
    print("✓ test_valid_diagnosis passed")


def test_missing_required_field():
    """Test: Missing root_cause field fails validation."""
    diagnosis = {
        "confidence": 80,
        "osi_layer": "Layer 3",
        "evidence": [],
        "next_command": "show ip route",
        "fix_steps": [],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert not is_valid, "Expected validation failure for missing root_cause"
    assert any("root_cause" in e for e in errors)
    print("✓ test_missing_required_field passed")


def test_confidence_out_of_range():
    """Test: Confidence > 100 fails validation."""
    diagnosis = {
        "root_cause": "Test",
        "confidence": 150,
        "osi_layer": "Layer 2",
        "evidence": [],
        "next_command": "",
        "fix_steps": [],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert not is_valid, "Expected validation failure for confidence > 100"
    print("✓ test_confidence_out_of_range passed")


def test_confidence_negative():
    """Test: Negative confidence fails validation."""
    diagnosis = {
        "root_cause": "Test",
        "confidence": -10,
        "osi_layer": "Layer 2",
        "evidence": [],
        "next_command": "",
        "fix_steps": [],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert not is_valid, "Expected validation failure for negative confidence"
    print("✓ test_confidence_negative passed")


def test_empty_root_cause():
    """Test: Empty root_cause fails validation."""
    diagnosis = {
        "root_cause": "",
        "confidence": 80,
        "osi_layer": "Layer 3",
        "evidence": [],
        "next_command": "",
        "fix_steps": [],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert not is_valid, "Expected validation failure for empty root_cause"
    print("✓ test_empty_root_cause passed")


def test_evidence_must_be_list():
    """Test: Evidence must be a list, not a string."""
    diagnosis = {
        "root_cause": "Test",
        "confidence": 80,
        "osi_layer": "Layer 3",
        "evidence": "This is a string, not a list",
        "next_command": "",
        "fix_steps": [],
        "alternative_causes": []
    }
    is_valid, errors = validate_diagnosis(diagnosis)
    assert not is_valid, "Expected validation failure for non-list evidence"
    print("✓ test_evidence_must_be_list passed")


def test_all_fields_missing():
    """Test: Completely empty dict fails validation."""
    is_valid, errors = validate_diagnosis({})
    assert not is_valid
    assert len(errors) >= 7, f"Expected at least 7 errors for empty dict, got {len(errors)}"
    print("✓ test_all_fields_missing passed")


if __name__ == "__main__":
    tests = [
        test_valid_diagnosis,
        test_missing_required_field,
        test_confidence_out_of_range,
        test_confidence_negative,
        test_empty_root_cause,
        test_evidence_must_be_list,
        test_all_fields_missing,
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
