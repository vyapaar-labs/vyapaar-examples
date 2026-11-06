"""A scripted fake LLM for the autonomous research-loop example.

Replays scripted responses in order so the AI research loop is fully
deterministic offline (mirroring the "cryptographic replayability" invariant of
the Vyapaar agent runtime).
"""

from __future__ import annotations

from collections.abc import Iterator


class ScriptedFakeLlm:
    """Deterministic LLM stand-in that returns the next scripted response."""

    def __init__(self, scripts: list[str]) -> None:
        self._scripts: Iterator[str] = iter(scripts)
        self.prompts: list[str] = []

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return next(self._scripts, "")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"ScriptedFakeLlm(scripts_left={sum(1 for _ in self._scripts)})"
