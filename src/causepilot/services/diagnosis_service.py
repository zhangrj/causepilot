from __future__ import annotations

from typing import Any
from ..agent.diagnosis_agent import DiagnosisAgent
from ..models.alert_event import AlertEvent
from ..models.diagnosis_result import DiagnosisResult
from ..mcp.client import MCPClient


class DiagnosisService:
    def __init__(self, mcp_client: MCPClient | None = None):
        self.mcp = mcp_client or MCPClient()
        self.agent = DiagnosisAgent(self.mcp)

    def diagnose(self, payload: Any) -> DiagnosisResult:
        # validate input via AlertEvent model
        alert = AlertEvent(**payload)
        return self.agent.diagnose(alert)
