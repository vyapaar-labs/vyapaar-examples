# mirror: kernel-verbatim port (gap 0002: ai.llm.provider surface)

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

__all__ = ["LlmPort", "ScriptedFakeLlm"]


class LlmPort(ABC):
    """Abstract interface for LLM completions."""

    @abstractmethod
    def complete(
        self,
        messages: Sequence[dict[str, str]],
        grammar: str | None = None,
        schema: dict[str, Any] | None = None,
        seed: int | None = None,
        temperature: float = 0.0,
    ) -> str:
        """Generate a completion for the given messages."""
        ...


class ScriptedFakeLlm(LlmPort):
    """Deterministic scripted LLM for testing and scaffolding."""

    def __init__(
        self,
        responses: Sequence[str | Exception] | None = None,
        default_response: str = "",
    ) -> None:
        self.responses = list(responses) if responses else []
        self.default_response = default_response
        self.call_history: list[dict[str, Any]] = []

    def complete(
        self,
        messages: Sequence[dict[str, str]],
        grammar: str | None = None,
        schema: dict[str, Any] | None = None,
        seed: int | None = None,
        temperature: float = 0.0,
    ) -> str:
        self.call_history.append(
            {
                "messages": list(messages),
                "grammar": grammar,
                "schema": schema,
                "seed": seed,
                "temperature": temperature,
            }
        )
        if self.responses:
            resp = self.responses.pop(0)
            if isinstance(resp, Exception):
                raise resp
            return resp
        return self.default_response

    def reset(self) -> None:
        self.call_history.clear()
