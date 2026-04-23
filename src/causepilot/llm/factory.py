from __future__ import annotations

import os
from typing import Any

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .registry import get_builder, register_builder


def _as_str(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _set_env_if_present(name: str, value: str) -> None:
    if value:
        os.environ[name] = value


def _normalize_provider(provider: str) -> str:
    """
    保持 .env 不变，但把内部 provider 名做归一化。
    例如：
    - gemini -> google
    """
    aliases = {
        "gemini": "google",
    }
    return aliases.get(provider.lower(), provider.lower())


def build_model(settings: Any):
    """
    将当前项目的通用 .env 配置，转换为 PydanticAI 可识别的模型引用：
    - 要么返回 '<provider>:<model>' 字符串
    - 要么返回显式构造的 Model 实例（例如 OpenAIChatModel）
    """
    provider = _normalize_provider(_as_str(settings.CAUSEPILOT_LLM_PROVIDER))
    builder = get_builder(provider)
    return builder(settings)


@register_builder("openai")
def _build_openai(settings: Any):
    """
    OpenAI / OpenAI-compatible 通用入口。
    你的 DashScope(qwen-plus) 场景会走这里：
    provider=openai, endpoint=https://dashscope.aliyuncs.com/compatible-mode/v1
    """
    model_name = _as_str(settings.CAUSEPILOT_LLM_MODEL)
    api_key = _as_str(getattr(settings, "CAUSEPILOT_LLM_API_KEY", ""))
    endpoint = _as_str(getattr(settings, "CAUSEPILOT_LLM_ENDPOINT", ""))

    if not model_name:
        raise ValueError("CAUSEPILOT_LLM_MODEL must not be empty")

    # 1) 有 endpoint => 走 OpenAI-compatible 显式 provider
    if endpoint:
        provider = OpenAIProvider(
            base_url=endpoint,
            api_key=api_key or None,
        )
        return OpenAIChatModel(model_name, provider=provider)

    # 2) 无 endpoint => 走标准 OpenAI provider:model 字符串
    _set_env_if_present("OPENAI_API_KEY", api_key)
    return f"openai:{model_name}"


@register_builder("ollama")
def _build_ollama(settings: Any):
    """
    Ollama 走 OpenAI-compatible 路线。
    若未配置 endpoint，则默认本地 Ollama OpenAI-compatible 地址。
    """
    model_name = _as_str(settings.CAUSEPILOT_LLM_MODEL)
    api_key = _as_str(getattr(settings, "CAUSEPILOT_LLM_API_KEY", ""))
    endpoint = _as_str(getattr(settings, "CAUSEPILOT_LLM_ENDPOINT", "")) or "http://localhost:11434/v1"

    if not model_name:
        raise ValueError("CAUSEPILOT_LLM_MODEL must not be empty")

    provider = OpenAIProvider(
        base_url=endpoint,
        # 很多本地 Ollama 场景并不校验 key，这里允许为空；必要时可填任意非空串
        api_key=api_key or None,
    )
    return OpenAIChatModel(model_name, provider=provider)


@register_builder("anthropic")
def _build_anthropic(settings: Any):
    """
    Anthropic 这里优先走 provider:model 字符串，由 PydanticAI 自己推断；
    同时把项目统一的 API_KEY 映射到 Anthropic 期望的环境变量。
    """
    model_name = _as_str(settings.CAUSEPILOT_LLM_MODEL)
    api_key = _as_str(getattr(settings, "CAUSEPILOT_LLM_API_KEY", ""))
    endpoint = _as_str(getattr(settings, "CAUSEPILOT_LLM_ENDPOINT", ""))

    if not model_name:
        raise ValueError("CAUSEPILOT_LLM_MODEL must not be empty")

    if endpoint:
        raise ValueError(
            "Custom endpoint for provider=anthropic is not implemented in the current factory. "
            "Please leave CAUSEPILOT_LLM_ENDPOINT empty for anthropic, or add a dedicated builder later."
        )

    _set_env_if_present("ANTHROPIC_API_KEY", api_key)
    return f"anthropic:{model_name}"


@register_builder("groq")
def _build_groq(settings: Any):
    model_name = _as_str(settings.CAUSEPILOT_LLM_MODEL)
    api_key = _as_str(getattr(settings, "CAUSEPILOT_LLM_API_KEY", ""))
    endpoint = _as_str(getattr(settings, "CAUSEPILOT_LLM_ENDPOINT", ""))

    if not model_name:
        raise ValueError("CAUSEPILOT_LLM_MODEL must not be empty")

    if endpoint:
        raise ValueError(
            "Custom endpoint for provider=groq is not implemented in the current factory. "
            "Please leave CAUSEPILOT_LLM_ENDPOINT empty for groq, or add a dedicated builder later."
        )

    _set_env_if_present("GROQ_API_KEY", api_key)
    return f"groq:{model_name}"


@register_builder("google")
def _build_google(settings: Any):
    """
    对外你仍然可以在 .env 写：
        CAUSEPILOT_LLM_PROVIDER=gemini
    工厂内部会把 gemini 归一化为 google。
    """
    model_name = _as_str(settings.CAUSEPILOT_LLM_MODEL)
    api_key = _as_str(getattr(settings, "CAUSEPILOT_LLM_API_KEY", ""))
    endpoint = _as_str(getattr(settings, "CAUSEPILOT_LLM_ENDPOINT", ""))

    if not model_name:
        raise ValueError("CAUSEPILOT_LLM_MODEL must not be empty")

    if endpoint:
        raise ValueError(
            "Custom endpoint for provider=gemini/google is not implemented in the current factory. "
            "Please leave CAUSEPILOT_LLM_ENDPOINT empty for gemini/google, or add a dedicated builder later."
        )

    _set_env_if_present("GEMINI_API_KEY", api_key)
    return f"google:{model_name}"