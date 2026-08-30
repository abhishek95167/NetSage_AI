"""
NetSage AI — Diagnosis Router
AI diagnosis and rule checker endpoints.
"""

import json
import sys
import os
from fastapi import APIRouter, HTTPException
from backend.database import execute_query, execute_insert

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ai.diagnosis.engine import get_engine
from rule_checker.main import run_all_checks, get_summary

router = APIRouter(prefix="/api/diagnosis", tags=["diagnosis"])


@router.post("/{case_id}/ai")
async def run_ai_diagnosis(case_id: str):
    """Run AI diagnosis on a case."""
    # Get the case
    rows = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not rows:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    case = rows[0]

    # Run AI diagnosis
    engine = get_engine()
    try:
        diagnosis = await engine.diagnose(
            symptom=case["symptom"],
            topology_notes=case["topology_notes"],
            show_outputs=case["show_outputs"],
            expected_fault=case.get("expected_fault", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI diagnosis failed: {str(e)}")

    # Store the diagnosis
    diag_id = await execute_insert(
        """INSERT INTO diagnoses (case_id, root_cause, confidence, osi_layer, evidence, 
           next_command, fix_steps, alternative_causes, is_demo_mode)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            case_id,
            diagnosis["root_cause"],
            diagnosis["confidence"],
            diagnosis["osi_layer"],
            json.dumps(diagnosis["evidence"]),
            diagnosis["next_command"],
            json.dumps(diagnosis["fix_steps"]),
            json.dumps(diagnosis["alternative_causes"]),
            1 if engine.is_demo_mode else 0
        )
    )

    # Update case status
    await execute_query(
        "UPDATE cases SET status = 'Analyzed', updated_at = datetime('now') WHERE case_id = ?",
        (case_id,)
    )

    return {
        "id": diag_id,
        "case_id": case_id,
        "is_demo_mode": engine.is_demo_mode,
        **diagnosis
    }


@router.post("/{case_id}/rule-check")
async def run_rule_check(case_id: str):
    """Run deterministic rule checker on a case."""
    rows = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not rows:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    case = rows[0]

    results = run_all_checks(
        show_output=case["show_outputs"],
        topology_notes=case["topology_notes"],
        symptom=case["symptom"]
    )

    summary = get_summary(results)

    # Store results
    await execute_insert(
        "INSERT INTO rule_check_results (case_id, results) VALUES (?, ?)",
        (case_id, json.dumps(results))
    )

    return {
        "case_id": case_id,
        "results": results,
        "summary": summary
    }


@router.get("/{case_id}")
async def get_diagnosis(case_id: str):
    """Get the latest diagnosis for a case."""
    rows = await execute_query(
        "SELECT * FROM diagnoses WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
        (case_id,)
    )
    if not rows:
        return None

    diag = rows[0]
    # Parse JSON fields
    diag["evidence"] = json.loads(diag.get("evidence", "[]"))
    diag["fix_steps"] = json.loads(diag.get("fix_steps", "[]"))
    diag["alternative_causes"] = json.loads(diag.get("alternative_causes", "[]"))
    diag["is_demo_mode"] = bool(diag.get("is_demo_mode", 0))

    return diag


@router.get("/{case_id}/rule-check")
async def get_rule_check(case_id: str):
    """Get the latest rule check results for a case."""
    rows = await execute_query(
        "SELECT * FROM rule_check_results WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
        (case_id,)
    )
    if not rows:
        return None

    result = rows[0]
    result["results"] = json.loads(result.get("results", "[]"))
    return result


@router.get("/{case_id}/history")
async def get_diagnosis_history(case_id: str):
    """Get all diagnoses for a case."""
    rows = await execute_query(
        "SELECT * FROM diagnoses WHERE case_id = ? ORDER BY created_at DESC",
        (case_id,)
    )
    for row in rows:
        row["evidence"] = json.loads(row.get("evidence", "[]"))
        row["fix_steps"] = json.loads(row.get("fix_steps", "[]"))
        row["alternative_causes"] = json.loads(row.get("alternative_causes", "[]"))
        row["is_demo_mode"] = bool(row.get("is_demo_mode", 0))
    return rows
