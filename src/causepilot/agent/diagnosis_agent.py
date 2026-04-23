from __future__ import annotations

import json
import logging

from pydantic_ai import Agent

from ..config.settings import settings
from ..llm.factory import build_model
from ..mcp.client import MCPClient
from ..models.alert_event import AlertEvent
from ..models.diagnosis_result import DiagnosisResult

logger = logging.getLogger(__name__)


class DiagnosisAgent:
    def __init__(self, mcp_client: MCPClient | None = None):
        self.mcp = mcp_client or MCPClient()
        self.max_calls = settings.CAUSEPILOT_MAX_TOOL_CALLS

        self.agent = Agent(
            build_model(settings),
            output_type=DiagnosisResult,
            instructions=(
                "You are CausePilot, a production-grade alert diagnosis agent.\n"
                "You must analyze the alert context and return ONLY a valid DiagnosisResult.\n"
                "Requirements:\n"
                "1. Output top 3 likely causes.\n"
                "2. Each cause must include a confidence score.\n"
                "3. Provide recommended investigation actions.\n"
                "4. If evidence is insufficient, lower confidence instead of inventing facts.\n"
                "5. Keep the answer concise, technical, and evidence-oriented.\n"
            ),
        )

    def diagnose(self, alert: AlertEvent) -> DiagnosisResult:
        return self._diagnose_with_pydantic_ai(alert)

    def _diagnose_with_pydantic_ai(self, alert: AlertEvent) -> DiagnosisResult:
        context = {
            "alert": alert.model_dump(),
            "mcp_server_url": str(settings.OBSERVE_MCP_SERVER_HTTP_URL),
            "max_tool_calls": self.max_calls,
        }

        prompt = self._build_prompt(context)

        try:
            result = self.agent.run_sync(prompt)
            return result.output
        except Exception as exc:
            logger.exception("pydantic_ai diagnosis failed: %s", exc)
            raise RuntimeError("pydantic_ai diagnosis failed") from exc

    @staticmethod
    def _build_prompt(context: dict) -> str:
        pretty_context = json.dumps(context, ensure_ascii=False, indent=2)
        return (
            "Diagnose the following production alert.\n\n"
            "Context:\n"
            f"{pretty_context}\n\n"
            "Return only a DiagnosisResult-compatible structured output."
        )