"""
NetSage AI — Human Review Workflow Tests
Tests the review submission and case status updates.
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import init_db, execute_query, execute_insert, execute_update, get_db, DATABASE_PATH


async def setup_test_db():
    """Set up a clean test database."""
    # Use a test database
    import backend.database as db_module
    db_module.DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_netsage.db")
    
    # Remove if exists
    if os.path.exists(db_module.DATABASE_PATH):
        os.remove(db_module.DATABASE_PATH)
    
    await init_db()
    
    # Insert a test case
    await execute_insert(
        """INSERT INTO cases (case_id, title, symptom, status) 
           VALUES ('TEST-001', 'Test Case', 'Test symptom', 'Open')"""
    )
    
    # Insert a test diagnosis
    await execute_insert(
        """INSERT INTO diagnoses (case_id, root_cause, confidence, osi_layer, evidence, next_command, fix_steps, alternative_causes) 
           VALUES ('TEST-001', 'Test root cause', 80, 'Layer 3', '[]', 'show ip route', '[]', '[]')"""
    )
    
    return db_module.DATABASE_PATH


async def test_accept_review():
    """Test: Accept review updates case status to Resolved."""
    db_path = await setup_test_db()
    
    try:
        # Get diagnosis
        diags = await execute_query("SELECT id FROM diagnoses WHERE case_id = 'TEST-001'")
        diag_id = diags[0]["id"]
        
        # Submit accept review
        review_id = await execute_insert(
            """INSERT INTO reviews (case_id, diagnosis_id, decision, reviewer_notes) 
               VALUES ('TEST-001', ?, 'accepted', 'Correct diagnosis')""",
            (diag_id,)
        )
        
        # Update case status
        await execute_update(
            "UPDATE cases SET status = 'Resolved' WHERE case_id = 'TEST-001'"
        )
        
        # Verify
        cases = await execute_query("SELECT status FROM cases WHERE case_id = 'TEST-001'")
        assert cases[0]["status"] == "Resolved", f"Expected Resolved, got {cases[0]['status']}"
        
        reviews = await execute_query("SELECT * FROM reviews WHERE case_id = 'TEST-001'")
        assert len(reviews) == 1
        assert reviews[0]["decision"] == "accepted"
        
        print("✓ test_accept_review passed")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


async def test_edit_review():
    """Test: Edit review stores edited diagnosis."""
    db_path = await setup_test_db()
    
    try:
        diags = await execute_query("SELECT id FROM diagnoses WHERE case_id = 'TEST-001'")
        diag_id = diags[0]["id"]
        
        edited_text = "The actual root cause is a gateway mismatch"
        review_id = await execute_insert(
            """INSERT INTO reviews (case_id, diagnosis_id, decision, edited_diagnosis, reviewer_notes) 
               VALUES ('TEST-001', ?, 'edited', ?, 'AI was partially wrong')""",
            (diag_id, edited_text)
        )
        
        reviews = await execute_query("SELECT * FROM reviews WHERE case_id = 'TEST-001'")
        assert len(reviews) == 1
        assert reviews[0]["decision"] == "edited"
        assert reviews[0]["edited_diagnosis"] == edited_text
        
        print("✓ test_edit_review passed")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


async def test_reject_review():
    """Test: Reject review updates case status to Rejected."""
    db_path = await setup_test_db()
    
    try:
        diags = await execute_query("SELECT id FROM diagnoses WHERE case_id = 'TEST-001'")
        diag_id = diags[0]["id"]
        
        await execute_insert(
            """INSERT INTO reviews (case_id, diagnosis_id, decision, reviewer_notes) 
               VALUES ('TEST-001', ?, 'rejected', 'Completely wrong diagnosis')""",
            (diag_id,)
        )
        
        await execute_update(
            "UPDATE cases SET status = 'Rejected' WHERE case_id = 'TEST-001'"
        )
        
        cases = await execute_query("SELECT status FROM cases WHERE case_id = 'TEST-001'")
        assert cases[0]["status"] == "Rejected"
        
        print("✓ test_reject_review passed")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


async def test_multiple_reviews():
    """Test: Multiple reviews can be submitted for same case."""
    db_path = await setup_test_db()
    
    try:
        diags = await execute_query("SELECT id FROM diagnoses WHERE case_id = 'TEST-001'")
        diag_id = diags[0]["id"]
        
        # Submit first review (reject)
        await execute_insert(
            """INSERT INTO reviews (case_id, diagnosis_id, decision, reviewer_notes) 
               VALUES ('TEST-001', ?, 'rejected', 'First review')""",
            (diag_id,)
        )
        
        # Submit second review (accept)
        await execute_insert(
            """INSERT INTO reviews (case_id, diagnosis_id, decision, reviewer_notes) 
               VALUES ('TEST-001', ?, 'accepted', 'Second review after fix')""",
            (diag_id,)
        )
        
        reviews = await execute_query("SELECT * FROM reviews WHERE case_id = 'TEST-001' ORDER BY id")
        assert len(reviews) == 2
        assert reviews[0]["decision"] == "rejected"
        assert reviews[1]["decision"] == "accepted"
        
        print("✓ test_multiple_reviews passed")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def run_async_test(coro):
    """Helper to run async test."""
    asyncio.run(coro)


if __name__ == "__main__":
    tests = [
        ("test_accept_review", test_accept_review),
        ("test_edit_review", test_edit_review),
        ("test_reject_review", test_reject_review),
        ("test_multiple_reviews", test_multiple_reviews),
    ]
    
    passed = 0
    failed = 0
    for name, test in tests:
        try:
            run_async_test(test())
            passed += 1
        except AssertionError as e:
            print(f"✗ {name} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'='*50}")
