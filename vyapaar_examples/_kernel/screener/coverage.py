# mirror: kernel-verbatim port (gap 0003: screener coverage surface)

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = ["Coverage", "DateInterval"]


@dataclass(frozen=True)
class DateInterval:
    """A date interval for coverage queries."""

    start: date
    end: date


class Coverage:
    """Coverage data for screener queries."""

    def __init__(self) -> None:
        self._data: dict[str, list[DateInterval]] = {}

    def add(self, symbol: str, interval: DateInterval) -> None:
        self._data.setdefault(symbol, []).append(interval)

    def intervals(self, symbol: str) -> list[DateInterval]:
        return self._data.get(symbol, [])
