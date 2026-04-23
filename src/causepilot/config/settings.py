from __future__ import annotations

from typing import Optional

from pydantic import AnyHttpUrl

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # MCP server configuration
    OBSERVE_MCP_SERVER_HTTP_URL: Optional[AnyHttpUrl] = None
    # optional auth
    OBSERVE_MCP_BEARER_TOKEN: str | None = None

    # LLM configuration (provider/model and credentials)
    CAUSEPILOT_LLM_PROVIDER: str = "mock"
    CAUSEPILOT_LLM_MODEL: str | None = None
    CAUSEPILOT_LLM_API_KEY: str | None = None
    CAUSEPILOT_LLM_API_SECRET: str | None = None
    CAUSEPILOT_LLM_ENDPOINT: str | None = None

    # runtime
    CAUSEPILOT_REQUEST_TIMEOUT: int = 10
    CAUSEPILOT_MAX_TOOL_CALLS: int = 20
    CAUSEPILOT_LOG_LEVEL: str = "INFO"
    CAUSEPILOT_BIND_HOST: str = "0.0.0.0"
    CAUSEPILOT_BIND_PORT: int = 8080

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
