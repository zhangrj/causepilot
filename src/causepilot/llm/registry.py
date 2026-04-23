from __future__ import annotations

from collections.abc import Callable
from typing import Any

ModelLike = Any
ModelBuilder = Callable[[Any], ModelLike]

_BUILDERS: dict[str, ModelBuilder] = {}


def register_builder(*provider_names: str):
    def decorator(func: ModelBuilder) -> ModelBuilder:
        for name in provider_names:
            _BUILDERS[name.lower()] = func
        return func

    return decorator


def get_builder(provider_name: str) -> ModelBuilder:
    key = provider_name.lower()
    try:
        return _BUILDERS[key]
    except KeyError as exc:
        supported = ", ".join(sorted(_BUILDERS.keys()))
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. Supported providers: {supported}"
        ) from exc


def available_builders() -> tuple[str, ...]:
    return tuple(sorted(_BUILDERS.keys()))