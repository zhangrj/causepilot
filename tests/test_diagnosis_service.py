from causepilot.services.diagnosis_service import DiagnosisService


def test_diagnose_minimal(monkeypatch):
    # Prepare a fake pydantic_ai runtime that returns a DiagnosisResult-shaped dict
    class FakePydanticAI:
        @staticmethod
        def run(schema=None, input=None, config=None):
            return {
                "incident_type": "latency_spike",
                "summary": "fake summary",
                "top_causes": [
                    {"rank": 1, "cause_code": "downstream_dependency_slow", "title": "下游依赖响应变慢", "confidence": 0.8, "evidence": ["e1"], "recommended_checks": ["c1"]},
                    {"rank": 2, "cause_code": "connection_pool_exhaustion", "title": "连接池问题", "confidence": 0.4, "evidence": ["e2"], "recommended_checks": ["c2"]},
                    {"rank": 3, "cause_code": "release_regression", "title": "发布回归", "confidence": 0.2, "evidence": ["e3"], "recommended_checks": ["c3"]},
                ],
                "recommended_action": ["check downstream"]
            }

    import causepilot.agent.diagnosis_agent as da

    # inject fake runtime and mark available before creating service
    monkeypatch.setattr(da, "pydantic_ai", FakePydanticAI)
    monkeypatch.setattr(da, "PydanticAI_AVAILABLE", True)

    service = DiagnosisService()

    # mock MCP client to avoid real HTTP calls
    class FakeMCP:
        def call_tool(self, tool, params):
            return {"summary": "fake"}

    service.mcp = FakeMCP()
    payload = {
        "title": "checkout-service p95 latency high",
        "severity": "critical",
        "service": "checkout-service",
        "environment": "prod",
        "metric": "http_server_duration_p95",
        "window_start": "2026-04-20T08:00:00Z",
        "window_end": "2026-04-20T08:15:00Z",
    }
    res = service.diagnose(payload)
    assert hasattr(res, 'top_causes')
