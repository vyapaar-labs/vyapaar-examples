# mirror: kernel-verbatim port (gap 0003: vyapaar-data quantity query)

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

__all__ = ["Quantity", "QuantityError", "parse_quantity"]


class QuantityError(ValueError):
    """Raised when a quantity string cannot be parsed."""


@dataclass(frozen=True)
class Quantity:
    """Parsed quantity representing an evaluated numeric value and metadata."""

    value: float
    raw_number: float = 0.0
    unit_suffix: str | None = None
    currency: str | None = None

    def __iter__(self) -> Iterator[Any]:
        return iter((Decimal(str(self.value)), self.unit_suffix or "shares"))

    def __getitem__(self, index: int) -> Any:
        return (Decimal(str(self.value)), self.unit_suffix or "shares")[index]


def parse_quantity(qty_str: str, market: str | None = None) -> Quantity:
    """Parse a quantity string into a Quantity object.

    Also unpacks as a tuple of (Decimal, unit) for backward compatibility.
    """
    qty_str = qty_str.strip()
    if not qty_str:
        raise QuantityError("empty quantity string")

    # Strip commas in numbers like 25,000 or 1,00,000
    cleaned = re.sub(r"(?<=\d),(?=\d)", "", qty_str).lower()

    mult_map: dict[str, float] = {
        "cr": 10_000_000.0,
        "crore": 10_000_000.0,
        "crores": 10_000_000.0,
        "lk": 100_000.0,
        "l": 100_000.0,
        "lakh": 100_000.0,
        "lakhs": 100_000.0,
        "k": 1_000.0,
        "thousand": 1_000.0,
        "m": 1_000_000.0,
        "mn": 1_000_000.0,
        "million": 1_000_000.0,
        "b": 1_000_000_000.0,
        "bn": 1_000_000_000.0,
        "billion": 1_000_000_000.0,
        "t": 1_000_000_000_000.0,
        "tn": 1_000_000_000_000.0,
        "trillion": 1_000_000_000_000.0,
        "%": 0.01,
        "pct": 0.01,
        "percent": 0.01,
    }

    # Match numeric part and suffix
    m = re.match(r"^([\+\-]?(?:\d+(?:\.\d*)?|\.\d+))\s*(.*)$", cleaned)
    if not m:
        raise QuantityError(f"invalid quantity string: {qty_str!r}")

    num_part, suffix_part = m.groups()
    try:
        raw_val = float(num_part)
    except ValueError as exc:
        raise QuantityError(f"invalid number {num_part!r}") from exc

    suffix = suffix_part.strip()
    mult = 1.0
    if suffix:
        if suffix in mult_map:
            mult = mult_map[suffix]
        else:
            raise QuantityError(f"unknown suffix {suffix!r}")

    final_val = raw_val * mult
    return Quantity(value=final_val, raw_number=raw_val, unit_suffix=suffix or "shares")
