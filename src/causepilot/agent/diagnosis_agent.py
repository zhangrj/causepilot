from __future__ import annotations

from typing import List
from ..models.alert_event import AlertEvent
from ..models.diagnosis_result import DiagnosisResult, TopCause
from ..mcp.client import MCPClient
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)
try:
    import pydantic_ai as pydantic_ai  # type: ignore
    PydanticAI_AVAILABLE = True
    _IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - runtime dependency
    pydantic_ai = None
    PydanticAI_AVAILABLE = False
    _IMPORT_ERROR = exc


class DiagnosisAgent:
    def __init__(self, mcp_client: MCPClient | None = None):
        self.mcp = mcp_client or MCPClient()
        self.max_calls = settings.CAUSEPILOT_MAX_TOOL_CALLS
        # Enforce usage of PydanticAI. Fail fast if not available.
        if not PydanticAI_AVAILABLE:
            raise RuntimeError(f"pydantic_ai is required for DiagnosisAgent but is not available: {_IMPORT_ERROR}")

        self.use_pydantic_ai = True

    def diagnose(self, alert: AlertEvent) -> DiagnosisResult:
        """Diagnosis entrypoint — uses PydanticAI implementation per spec.

        This method calls into the PydanticAI runtime and expects a
        `DiagnosisResult`-compatible object (or dict). Per requirement,
        there is no heuristic fallback; failures are surfaced to caller.
        """
        return self._diagnose_with_pydantic_ai(alert)

    def _diagnose_with_pydantic_ai(self, alert: AlertEvent) -> DiagnosisResult:
        """Run PydanticAI-driven diagnosis.

        The implementation attempts a couple of commonly-used PydanticAI
        entrypoints (`run`, or an `Agent` class with `invoke`). It passes
        the alert context and LLM/provider credentials from settings.
        If none of the supported APIs return a usable result, a
        RuntimeError is raised.
        """
        if not PydanticAI_AVAILABLE:
            raise RuntimeError("pydantic_ai not available")

        context = {
            "alert": alert.model_dump(),
            "mcp_server_url": str(settings.CAUSEPILOT_OBSERVE_MCP_SERVER_URL),
            "max_tool_calls": settings.CAUSEPILOT_MAX_TOOL_CALLS,
        }

        run_kwargs = {
            "schema": DiagnosisResult,
            "input": context,
            "config": {
                "provider": settings.CAUSEPILOT_LLM_PROVIDER,
                "model": settings.CAUSEPILOT_LLM_MODEL,
                "api_key": settings.CAUSEPILOT_LLM_API_KEY,
                "api_secret": settings.CAUSEPILOT_LLM_API_SECRET,
                "endpoint": settings.CAUSEPILOT_LLM_ENDPOINT,
            },
        }

        # 1) Try pydantic_ai.run
        try:
            if hasattr(pydantic_ai, "run"):
                result = pydantic_ai.run(**run_kwargs)
                if isinstance(result, DiagnosisResult):
                    return result
                if isinstance(result, dict):
                    return DiagnosisResult(**result)
        except Exception as exc:
            logger.exception("pydantic_ai.run failed: %s", exc)

        # 2) Try Agent-style invocation
        try:
            AgentCls = getattr(pydantic_ai, "Agent", None) or getattr(pydantic_ai, "PydanticAIAgent", None)
            if AgentCls:
                agent = AgentCls(provider=settings.CAUSEPILOT_LLM_PROVIDER, model=settings.CAUSEPILOT_LLM_MODEL, api_key=settings.CAUSEPILOT_LLM_API_KEY, api_secret=settings.CAUSEPILOT_LLM_API_SECRET, endpoint=settings.CAUSEPILOT_LLM_ENDPOINT)
                if hasattr(agent, "invoke"):
                    out = agent.invoke(context, output_model=DiagnosisResult)
                    if isinstance(out, DiagnosisResult):
                        return out
                    if isinstance(out, dict):
                        return DiagnosisResult(**out)
        except Exception as exc:
            logger.exception("pydantic_ai Agent invocation failed: %s", exc)

        # Strict: must return a structured result via PydanticAI
        raise RuntimeError("pydantic_ai invocation did not return a DiagnosisResult or usable dict")
