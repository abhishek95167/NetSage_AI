"""
NetSage AI — Dashboard Router
Dashboard statistics and analytics endpoints.
"""

import json
from fastapi import APIRouter
from backend.database import execute_query

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics."""
    # Total cases
    total = await execute_query("SELECT COUNT(*) as count FROM cases")
    total_cases = total[0]["count"]

    # Cases by status
    analyzed = await execute_query("SELECT COUNT(*) as count FROM cases WHERE status IN ('Analyzed', 'Resolved', 'Rejected')")
    analyzed_cases = analyzed[0]["count"]

    # Reviews breakdown
    accepted = await execute_query("SELECT COUNT(*) as count FROM reviews WHERE decision = 'accepted'")
    edited = await execute_query("SELECT COUNT(*) as count FROM reviews WHERE decision = 'edited'")
    rejected = await execute_query("SELECT COUNT(*) as count FROM reviews WHERE decision = 'rejected'")

    accepted_count = accepted[0]["count"]
    edited_count = edited[0]["count"]
    rejected_count = rejected[0]["count"]
    total_reviews = accepted_count + edited_count + rejected_count

    # Agreement rate
    agreement_rate = (accepted_count / total_reviews * 100) if total_reviews > 0 else 0

    # Cases by type (concept)
    type_rows = await execute_query(
        "SELECT concept, COUNT(*) as count FROM cases WHERE concept != '' GROUP BY concept"
    )
    cases_by_type = {row["concept"]: row["count"] for row in type_rows}

    # Cases by severity
    sev_rows = await execute_query(
        "SELECT severity, COUNT(*) as count FROM cases GROUP BY severity"
    )
    cases_by_severity = {row["severity"]: row["count"] for row in sev_rows}

    # Cases by OSI layer
    osi_rows = await execute_query(
        "SELECT osi_layer, COUNT(*) as count FROM cases WHERE osi_layer != '' GROUP BY osi_layer"
    )
    cases_by_osi_layer = {row["osi_layer"]: row["count"] for row in osi_rows}

    # Recent cases
    recent = await execute_query(
        "SELECT case_id, title, status, severity, concept, osi_layer, created_at FROM cases ORDER BY created_at DESC LIMIT 10"
    )

    return {
        "total_cases": total_cases,
        "analyzed_cases": analyzed_cases,
        "accepted_diagnoses": accepted_count,
        "edited_diagnoses": edited_count,
        "rejected_diagnoses": rejected_count,
        "agreement_rate": round(agreement_rate, 1),
        "cases_by_type": cases_by_type,
        "cases_by_severity": cases_by_severity,
        "cases_by_osi_layer": cases_by_osi_layer,
        "recent_cases": recent,
        "total_reviews": total_reviews
    }


@router.get("/analytics")
async def get_analytics():
    """Get detailed analytics data for charts."""
    # Issue type distribution
    type_rows = await execute_query(
        "SELECT concept, COUNT(*) as count FROM cases WHERE concept != '' GROUP BY concept ORDER BY count DESC"
    )

    # Severity distribution
    sev_rows = await execute_query(
        "SELECT severity, COUNT(*) as count FROM cases GROUP BY severity"
    )

    # OSI layer distribution
    osi_rows = await execute_query(
        "SELECT osi_layer, COUNT(*) as count FROM cases WHERE osi_layer != '' GROUP BY osi_layer"
    )

    # AI vs Human decisions
    review_rows = await execute_query(
        "SELECT decision, COUNT(*) as count FROM reviews GROUP BY decision"
    )

    # Most common root causes (from diagnoses)
    root_cause_rows = await execute_query(
        """SELECT root_cause, COUNT(*) as count FROM diagnoses 
           GROUP BY root_cause ORDER BY count DESC LIMIT 10"""
    )

    # Reviews over time (group by date)
    timeline_rows = await execute_query(
        """SELECT date(created_at) as date, decision, COUNT(*) as count 
           FROM reviews GROUP BY date(created_at), decision ORDER BY date"""
    )

    return {
        "issue_types": [{"name": r["concept"], "count": r["count"]} for r in type_rows],
        "severity_distribution": [{"name": r["severity"], "count": r["count"]} for r in sev_rows],
        "osi_layers": [{"name": r["osi_layer"], "count": r["count"]} for r in osi_rows],
        "ai_vs_human": [{"name": r["decision"], "count": r["count"]} for r in review_rows],
        "common_root_causes": [{"cause": r["root_cause"][:80], "count": r["count"]} for r in root_cause_rows],
        "review_timeline": [{"date": r["date"], "decision": r["decision"], "count": r["count"]} for r in timeline_rows]
    }


@router.get("/responsible-ai")
async def get_responsible_ai_log():
    """Get responsible AI log entries."""
    rows = await execute_query(
        """SELECT ral.*, c.title as case_title
           FROM responsible_ai_log ral
           LEFT JOIN cases c ON ral.case_id = c.case_id
           ORDER BY ral.created_at DESC"""
    )
    return rows
