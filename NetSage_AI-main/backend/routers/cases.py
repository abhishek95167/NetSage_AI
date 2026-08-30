"""
NetSage AI — Cases Router
CRUD operations for troubleshooting cases.
"""

import json
from fastapi import APIRouter, HTTPException
from backend.models import CaseCreate, CaseUpdate
from backend.database import execute_query, execute_insert, execute_update

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("")
async def list_cases(status: str = None, concept: str = None, severity: str = None):
    """List all cases with optional filters."""
    query = "SELECT * FROM cases WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)
    if concept:
        query += " AND concept = ?"
        params.append(concept)
    if severity:
        query += " AND severity = ?"
        params.append(severity)

    query += " ORDER BY created_at DESC"
    return await execute_query(query, tuple(params))


@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get a single case by case_id."""
    rows = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not rows:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return rows[0]


@router.post("")
async def create_case(case: CaseCreate):
    """Create a new troubleshooting case."""
    # Generate next case ID
    rows = await execute_query("SELECT MAX(id) as max_id FROM cases")
    next_id = (rows[0]["max_id"] or 0) + 1
    case_id = f"CASE-{next_id:03d}"

    await execute_insert(
        """INSERT INTO cases (case_id, title, symptom, topology_notes, show_outputs, 
           expected_fault, osi_layer, concept, severity, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Open')""",
        (case_id, case.title, case.symptom, case.topology_notes, case.show_outputs,
         case.expected_fault, case.osi_layer, case.concept, case.severity)
    )

    return {"case_id": case_id, "message": "Case created successfully"}


@router.put("/{case_id}")
async def update_case(case_id: str, case: CaseUpdate):
    """Update an existing case."""
    # Check case exists
    existing = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not existing:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    updates = []
    params = []

    for field, value in case.model_dump(exclude_unset=True).items():
        if value is not None:
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates.append("updated_at = datetime('now')")
    params.append(case_id)

    query = f"UPDATE cases SET {', '.join(updates)} WHERE case_id = ?"
    await execute_update(query, tuple(params))

    return {"message": f"Case {case_id} updated successfully"}


@router.delete("/{case_id}")
async def delete_case(case_id: str):
    """Delete a case and all related data."""
    existing = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not existing:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    await execute_update("DELETE FROM reviews WHERE case_id = ?", (case_id,))
    await execute_update("DELETE FROM diagnoses WHERE case_id = ?", (case_id,))
    await execute_update("DELETE FROM rule_check_results WHERE case_id = ?", (case_id,))
    await execute_update("DELETE FROM cases WHERE case_id = ?", (case_id,))

    return {"message": f"Case {case_id} deleted successfully"}
