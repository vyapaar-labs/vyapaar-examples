"""Synthetic data: deterministic bars generated in integer paise.

The zero-floats invariant starts at the source: random walks step in integer
paise (``random.randint``) and prices are materialized as exact
``decimal.Decimal`` values. No ``float`` ever represents a price.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

PAISE = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class Bar:
    """One OHLCV bar with exact ``Decimal`` prices."""

    instrument: str
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int = 0
    interval: str = "1d"

    def __post_init__(self) -> None:
        if self.high < self.low:
            raise ValueError("high must be >= low")


class SampleInstruments(StrEnum):
    """Canonical instruments used across the examples."""

    NIFTY50 = "NSE:NIFTY50-INDEX"
    BANKNIFTY = "NSE:BANKNIFTY-INDEX"
    RELIANCE = "NSE:RELIANCE-EQ"
    INFY = "NSE:INFY-EQ"
    TCS = "NSE:TCS-EQ"


def _to_utc(day: date, hour: int = 0) -> datetime:
    return datetime(day.year, day.month, day.day, hour, tzinfo=UTC)


def synthetic_bars(
    instrument: str,
    days: int = 250,
    start: date | None = None,
    seed: int = 42,
    base_price_paise: int = 10_000,
    daily_step_paise: int = 200,
    volume: int = 1_000_000,
) -> list[Bar]:
    """Generate a deterministic daily OHLC walk for an instrument.

    Prices step by ``daily_step_paise`` integer paise per day around
    ``base_price_paise``, seeded for reproducibility. The first bar's open is
    the base price.
    """
    if days <= 0:
        raise ValueError("days must be positive")
    rng = random.Random(seed)
    first_day = start or date(2024, 1, 1)
    bars: list[Bar] = []
    close_paise = base_price_paise
    for offset in range(days):
        ts = _to_utc(first_day + timedelta(days=offset))
        open_paise = base_price_paise if offset == 0 else close_paise
        close_paise = max(100, open_paise + rng.randint(-daily_step_paise, daily_step_paise))
        high_paise = max(open_paise, close_paise) + rng.randint(0, daily_step_paise // 4)
        low_paise = min(open_paise, close_paise) - rng.randint(0, daily_step_paise // 4)
        bars.append(
            Bar(
                instrument=instrument,
                ts=ts,
                open=Decimal(open_paise) * PAISE,
                high=Decimal(high_paise) * PAISE,
                low=Decimal(low_paise) * PAISE,
                close=Decimal(close_paise) * PAISE,
                volume=volume,
            )
        )
    return bars


def trending_bars(
    instrument: str,
    days: int = 120,
    start: date | None = None,
    base: Decimal | str = "100.00",
    step: Decimal | str = "0.50",
) -> list[Bar]:
    """A clean monotonic trend for signal-demonstration examples."""
    first_day = start or date(2024, 1, 1)
    base_decimal = base if isinstance(base, Decimal) else Decimal(str(base))
    step_decimal = step if isinstance(step, Decimal) else Decimal(str(step))
    return [
        Bar(
            instrument=instrument,
            ts=_to_utc(first_day + timedelta(days=i)),
            open=base_decimal + step_decimal * Decimal(i),
            high=base_decimal + step_decimal * Decimal(i) + Decimal("1"),
            low=base_decimal + step_decimal * Decimal(i) - Decimal("1"),
            close=base_decimal + step_decimal * Decimal(i),
        )
        for i in range(days)
    ]
