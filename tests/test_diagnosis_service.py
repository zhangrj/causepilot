from causepilot.services.diagnosis_service import DiagnosisService
from typing import cast
from causepilot.mcp.client import MCPClient


def test_diagnose_minimal(monkeypatch):
    # Prepare a fake pydantic_ai.Agent implementation that returns a DiagnosisResult-shaped dict
    class FakeAgent:
        def __init__(self, *args, **kwargs):
            pass
        def run_sync(self, prompt: str):
            # mirror pydantic_ai.Agent.run_sync behaviour: return object with `output` attribute
            data = {
                "incident_type": "latency_spike",
                "summary": "fake summary",
                "top_causes": [
                    {"rank": 1, "cause_code": "downstream_dependency_slow", "title": "下游依赖响应变慢", "confidence": 0.8, "evidence": ["e1"], "recommended_checks": ["c1"]},
                    {"rank": 2, "cause_code": "connection_pool_exhaustion", "title": "连接池问题", "confidence": 0.4, "evidence": ["e2"], "recommended_checks": ["c2"]},
                    {"rank": 3, "cause_code": "release_regression", "title": "发布回归", "confidence": 0.2, "evidence": ["e3"], "recommended_checks": ["c3"]},
                ],
                "recommended_action": ["check downstream"],
            }
            from types import SimpleNamespace
            from causepilot.models.diagnosis_result import DiagnosisResult

            # return object with `.output` set to a DiagnosisResult instance
            return SimpleNamespace(output=DiagnosisResult.model_validate(data))

    import types
    import causepilot.agent.diagnosis_agent as da

    # replace the imported Agent symbol in the module
    monkeypatch.setattr(da, "Agent", FakeAgent)
    # avoid JSON serialization of datetime in AlertEvent by stubbing prompt builder
    monkeypatch.setattr(da.DiagnosisAgent, "_build_prompt", lambda self, context: "prompt")

    service = DiagnosisService()

    # mock MCP client to avoid real HTTP calls
    class FakeMCP:
        def call_tool(self, tool, params):
            return {"summary": "fake"}

    service.mcp = cast(MCPClient, FakeMCP())
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
