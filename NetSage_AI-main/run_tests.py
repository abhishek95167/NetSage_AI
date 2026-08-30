"""
NetSage AI — Unified Test Runner
Runs all unit tests and test suites with proper UTF-8 handling on all platforms.
"""

import sys
import os
import io

# Set UTF-8 encoding for standard streams
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("=" * 60)
    print("  NETSAGE AI — FULL TEST SUITE RUNNER")
    print("=" * 60)
    
    test_files = [
        ("Deterministic Rule Checker", "tests/test_rule_checker.py"),
        ("AI Schema Validation", "tests/test_ai_schema.py"),
        ("Human Review Workflow", "tests/test_reviews.py"),
        ("AI-Human Agreement Rate", "tests/test_agreement.py"),
    ]

    import subprocess

    total_passed = 0
    total_failed = 0

    for name, filepath in test_files:
        print(f"\n▶ Running: {name} ({filepath})")
        print("-" * 50)
        
        result = subprocess.run(
            [sys.executable, "-X", "utf8", filepath],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False
        )
        if result.returncode == 0:
            total_passed += 1
        else:
            total_failed += 1

    print("\n" + "=" * 60)
    print(f"  ALL TEST SUITES COMPLETED ({total_passed}/{len(test_files)} passed)")
    print("=" * 60)



if __name__ == "__main__":
    main()
