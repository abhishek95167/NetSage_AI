"""
NetSage AI — Pydantic Models
Data validation models for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Case Models ---

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    symptom: str = Field(..., min_length=1)
    topology_notes: str = ""
    show_outputs: str = ""
    expected_fault: str = ""
    osi_layer: str = ""
    concept: str = ""
    severity: str = "Medium"


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    symptom: Optional[str] = None
    topology_notes: Optional[str] = None
    show_outputs: Optional[str] = None
    expected_fault: Optional[str] = None
    osi_layer: Optional[str] = None
    concept: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None


class CaseResponse(BaseModel):
    id: int
    case_id: str
    title: str
    symptom: str
    topology_notes: str
    show_outputs: str
    expected_fault: str
    osi_layer: str
    concept: str
    severity: str
    status: str
    created_at: str
    updated_at: str


# --- Diagnosis Models ---

class DiagnosisResult(BaseModel):
    root_cause: str
    confidence: int = Field(ge=0, le=100)
    osi_layer: str
    evidence: List[str] = []
    next_command: str = ""
    fix_steps: List[str] = []
    alternative_causes: List[str] = []


class DiagnosisResponse(BaseModel):
    id: int
    case_id: str
    root_cause: str
    confidence: int
    osi_layer: str
    evidence: List[str]
    next_command: str
    fix_steps: List[str]
    alternative_causes: List[str]
    is_demo_mode: bool
    created_at: str


# --- Review Models ---

class ReviewCreate(BaseModel):
    decision: str = Field(..., pattern="^(accepted|edited|rejected)$")
    edited_diagnosis: str = ""
    reviewer_notes: str = ""


class ReviewResponse(BaseModel):
    id: int
    case_id: str
    diagnosis_id: int
    decision: str
    edited_diagnosis: str
    reviewer_notes: str
    created_at: str


# --- Rule Checker Models ---

class RuleCheckResult(BaseModel):
    check: str
    status: str  # PASS or FAIL
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    evidence: str = ""
    message: str = ""


# --- Dashboard Models ---

class DashboardStats(BaseModel):
    total_cases: int
    analyzed_cases: int
    accepted_diagnoses: int
    edited_diagnoses: int
    rejected_diagnoses: int
    agreement_rate: float
    cases_by_type: dict
    cases_by_severity: dict
    cases_by_osi_layer: dict
    recent_cases: list


# --- Responsible AI Models ---

class ResponsibleAIEntry(BaseModel):
    id: int
    case_id: str
    ai_diagnosis: str
    human_correction: str
    why_ai_wrong: str
    final_diagnosis: str
    lesson: str
    created_at: str
