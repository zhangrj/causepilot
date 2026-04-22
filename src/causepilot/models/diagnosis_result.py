from __future__ import annotations

from typing import List
from pydantic import BaseModel


class TopCause(BaseModel):
    rank: int
    cause_code: str
    title: str
    confidence: float
    evidence: List[str]
    recommended_checks: List[str]


class DiagnosisResult(BaseModel):
    incident_type: str
    summary: str
    top_causes: List[TopCause]
    recommended_action: List[str]
