# CausePilot

Minimal Phase 1 implementation skeleton. To install runtime dependencies (managed by `uv`), run:

```powershell
uv add httpx pydantic pydantic-settings python-dotenv fastapi uvicorn pytest
# optional: add your LLM client, e.g. openai
uv add openai
```

Create a local `.env` from `.env.example` and edit endpoints as needed.

Configure LLM provider and credentials in `.env` when using PydanticAI:

```
CAUSEPILOT_LLM_PROVIDER=openai
CAUSEPILOT_LLM_MODEL=gpt-4o
CAUSEPILOT_LLM_API_KEY=your_api_key_here
CAUSEPILOT_LLM_API_SECRET=your_api_secret_here
CAUSEPILOT_LLM_ENDPOINT=https://api.openai.com
OBSERVE_MCP_BEARER_TOKEN=optional_mcp_api_key
```

Run the minimal API:

```powershell
python -m uv run causepilot
# or run uvicorn directly:
uv run -- uvicorn causepilot.main:app --host 0.0.0.0 --port 8000
```

Run tests:

```powershell
uv sync --extra tests
uv run pytest -q
```
