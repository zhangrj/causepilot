import pytest
from causepilot.mcp.client import MCPClient
from httpx import Response


def test_mcp_client_call_tool(monkeypatch):
    called = {}

    def fake_post(url, json):
        called['url'] = url
        assert 'tool' in json
        return Response(200, json={"summary": "ok"})

    class FakeClient:
        def post(self, url, json):
            return fake_post(url, json)

    client = MCPClient(base_url="http://localhost:8080")
    client._client = FakeClient()
    res = client.call_tool("metrics_query", {"metric": "m"})
    assert res.get('summary') == 'ok'
