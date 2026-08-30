"""
NetSage AI — Reviews Router
Human review workflow: Accept, Edit, or Reject AI diagnoses.
"""

import json
from fastapi import APIRouter, HTTPException
from backend.models import ReviewCreate
from backend.database import execute_query, execute_insert, execute_update

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("/{case_id}")
async def create_review(case_id: str, review: ReviewCreate):
    """Submit a human review for a case's AI diagnosis."""
    # Get the case
    case_rows = await execute_query("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    if not case_rows:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Get the latest diagnosis
    diag_rows = await execute_query(
        "SELECT * FROM diagnoses WHERE case_id = ? ORDER BY created_at DESC LIMIT 1",
        (case_id,)
    )
    if not diag_rows:
        raise HTTPException(status_code=400, detail=f"No diagnosis found for case {case_id}. Run AI diagnosis first.")

    diagnosis_id = diag_rows[0]["id"]

    # Insert the review
    review_id = await execute_insert(
        """INSERT INTO reviews (case_id, diagnosis_id, decision, edited_diagnosis, reviewer_notes)
           VALUES (?, ?, ?, ?, ?)""",
        (case_id, diagnosis_id, review.decision, review.edited_diagnosis, review.reviewer_notes)
    )

    # Update case status based on review decision
    status_map = {
        "accepted": "Resolved",
        "edited": "Resolved",
        "rejected": "Rejected"
    }
    new_status = status_map.get(review.decision, "Open")
    await execute_update(
        "UPDATE cases SET status = ?, updated_at = datetime('now') WHERE case_id = ?",
        (new_status, case_id)
    )

    return {
        "id": review_id,
        "case_id": case_id,
        "diagnosis_id": diagnosis_id,
        "decision": review.decision,
        "message": f"Review submitted: {review.decision}"
    }


@router.get("/{case_id}")
async def get_reviews(case_id: str):
    """Get all reviews for a case."""
    rows = await execute_query(
        "SELECT * FROM reviews WHERE case_id = ? ORDER BY created_at DESC",
        (case_id,)
    )
    return rows


@router.get("")
async def list_all_reviews():
    """List all reviews across all cases."""
    rows = await execute_query(
        """SELECT r.*, c.title as case_title 
           FROM reviews r 
           LEFT JOIN cases c ON r.case_id = c.case_id 
           ORDER BY r.created_at DESC"""
    )
    return rows
