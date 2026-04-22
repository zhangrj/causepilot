from __future__ import annotations

import httpx
from typing import Any, Dict
from ..config.settings import settings
import logging

logger = logging.getLogger(__name__)


class MCPClient:
    """Minimal MCP HTTP client wrapper. """

    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        self.base_url = base_url or str(settings.CAUSEPILOT_OBSERVE_MCP_SERVER_URL)
        self.timeout = timeout or settings.CAUSEPILOT_REQUEST_TIMEOUT
        headers = {}
        if settings.CAUSEPILOT_MCP_API_KEY:
            headers["Authorization"] = f"Bearer {settings.CAUSEPILOT_MCP_API_KEY}"
        self._client = httpx.Client(timeout=self.timeout, headers=headers)

    def call_tool(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a generic MCP tool by name. Returns parsed JSON or raises.

        Note: The exact MCP server endpoints may vary; this method assumes
        the MCP server exposes a POST /call_tool endpoint that accepts
        {"tool": "name", "params": {...}}. Adapt as needed for your server.
        """
        url = f"{self.base_url.rstrip('/')}/call_tool"
        payload = {"tool": tool, "params": params}
        logger.debug("Calling MCP tool %s -> %s", tool, url)
        import time

        start = time.perf_counter()
        try:
            r = self._client.post(url, json=payload)
            elapsed = time.perf_counter() - start
            logger.info("MCP call %s took %.3fs", tool, elapsed)
            # Some test doubles may return httpx.Response without a request attached,
            # so avoid calling raise_for_status() directly; check status_code instead.
            if getattr(r, "status_code", 0) >= 400:
                logger.warning("MCP tool call returned status %s", getattr(r, "status_code", None))
                raise httpx.HTTPError(f"MCP tool returned status {getattr(r, 'status_code', None)}")
            return r.json()
        except httpx.HTTPError as exc:
            elapsed = time.perf_counter() - start
            logger.warning("MCP tool call failed (%.3fs): %s", elapsed, exc)
            raise
