from causepilot.models.alert_event import AlertEvent
from causepilot.models.diagnosis_result import DiagnosisResult, TopCause
from datetime import datetime


def test_alert_event_validation():
    data = {
        "title": "checkout-service p95 latency high",
        "severity": "critical",
        "service": "checkout-service",
        "environment": "prod",
        "window_start": "2026-04-20T08:00:00Z",
        "window_end": "2026-04-20T08:15:00Z",
    }
    alert = AlertEvent(**data)
    assert alert.title.startswith("checkout-service")


def test_diagnosis_result_model():
    top = TopCause(rank=1, cause_code="c", title="t", confidence=0.5, evidence=["e"], recommended_checks=["r"])
    res = DiagnosisResult(incident_type="latency_spike", summary="s", top_causes=[top], recommended_action=["a"])
    assert res.top_causes[0].rank == 1
