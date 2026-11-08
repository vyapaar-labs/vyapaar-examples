"""LLM provider port and scripted fake (staged mirror of the kernel provider module).

Provides the abstract :class:`LlmPort` and one canonical :class:`ScriptedFakeLlm`
for deterministic testing and offline scaffolding when no local or remote LLM is
running. The unified class carries both APIs: the kernel port's
``complete(messages, grammar, schema, seed, temperature)`` contract and the
harness-side ``ask(prompt)`` convenience.
"""

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
        """Generate a completion for the given messages.

        Args:
            messages: List of chat messages (e.g. ``[{"role": "user", "content": "..."}]``).
            grammar: Optional GBNF/EBNF grammar string for constrained sampling.
            schema: Optional JSON schema for structured JSON output.
            seed: Optional random seed for reproducible completions.
            temperature: Sampling temperature (default 0.0 for deterministic).

        Returns:
            The raw string response from the model.
        """
        ...


class ScriptedFakeLlm(LlmPort):
    """Deterministic scripted LLM for testing and scaffolding.

    Returns pre-scripted ``responses`` sequentially (an ``Exception`` item is
    raised verbatim, to script repair loops), then falls back to
    ``default_response``. ``call_history`` records every ``complete`` call and
    ``prompts`` every ``ask`` call, so both entry points replay fully
    deterministic offline.
    """

    def __init__(
        self, responses: Sequence[str | Exception] | None = None, default_response: str = ""
    ) -> None:
        self.responses = list(responses) if responses else []
        self.default_response = default_response
        self.call_history: list[dict[str, Any]] = []
        self.prompts: list[str] = []

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

    def ask(self, prompt: str) -> str:
        """Harness convenience: record ``prompt`` and complete a single user message."""
        self.prompts.append(prompt)
        return self.complete([{"role": "user", "content": prompt}])

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ScriptedFakeLlm(scripts_left={len(self.responses)})"
