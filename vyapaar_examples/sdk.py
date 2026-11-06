"""Minimal Decimal indicators for the learning path.

These are compact, self-contained implementations used by the examples so they
stay deterministic without requiring the (separate) strategy SDK to be
installed. They mirror the streaming semantics of
``vyapaar_strategies.sdk.indicators`` for research-live parity.
"""

from __future__ import annotations

from decimal import Decimal


class SMA:
    """Simple moving average over the trailing ``period`` values."""

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self.period = period
        self._history: list[Decimal] = []

    def update(self, value: Decimal) -> None:
        self._history.append(value)

    @property
    def ready(self) -> bool:
        return len(self._history) >= self.period

    @property
    def value(self) -> Decimal:
        if not self.ready:
            raise ValueError("SMA is not ready")
        window = self._history[-self.period :]
        return sum(window, Decimal(0)) / Decimal(self.period)

    @property
    def previous_value(self) -> Decimal | None:
        if len(self._history) < self.period + 1:
            return None
        window = self._history[-self.period - 1 : -1]
        return sum(window, Decimal(0)) / Decimal(self.period)


class RSI:
    """Wilder's Relative Strength Index."""

    def __init__(self, period: int = 14) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self.period = period
        self._gains: list[Decimal] = []
        self._losses: list[Decimal] = []
        self._avg_gain: Decimal | None = None
        self._avg_loss: Decimal | None = None
        self._previous: Decimal | None = None

    def update(self, value: Decimal) -> None:
        previous = self._previous
        if previous is not None:
            change = value - previous
            gain = max(change, Decimal(0))
            loss = max(-change, Decimal(0))
            self._gains.append(gain)
            self._losses.append(loss)
            avg_gain = self._avg_gain
            avg_loss = self._avg_loss
            if avg_gain is None and len(self._gains) >= self.period:
                self._avg_gain = sum(self._gains[-self.period :], Decimal(0)) / Decimal(self.period)
                self._avg_loss = sum(self._losses[-self.period :], Decimal(0)) / Decimal(
                    self.period
                )
            elif avg_gain is not None and avg_loss is not None:
                self._avg_gain = (avg_gain * Decimal(self.period - 1) + gain) / Decimal(self.period)
                self._avg_loss = (avg_loss * Decimal(self.period - 1) + loss) / Decimal(self.period)
        self._previous = value

    @property
    def ready(self) -> bool:
        return self._avg_gain is not None

    @property
    def value(self) -> Decimal:
        if self._avg_gain is None or self._avg_loss is None:
            raise ValueError("RSI is not ready")
        if self._avg_loss == 0:
            return Decimal(100)
        relative_strength = self._avg_gain / self._avg_loss
        return Decimal(100) - Decimal(100) / (Decimal(1) + relative_strength)


def crosses_above(fast: SMA, slow: SMA) -> bool:
    """True when ``fast`` crossed above ``slow`` on the latest update."""
    fast_prev = fast.previous_value
    slow_prev = slow.previous_value
    return bool(
        fast.ready
        and slow.ready
        and fast_prev is not None
        and slow_prev is not None
        and fast_prev <= slow_prev
        and fast.value > slow.value
    )
