"""Shared helpers exercised by the examples must stay exact."""

from __future__ import annotations

from decimal import Decimal
from itertools import pairwise

from vyapaar_examples import (
    SMA,
    Backtest,
    SampleInstruments,
    compute_metrics,
    synthetic_bars,
)


def test_synthetic_bars_are_exact_decimal_prices() -> None:
    bars = synthetic_bars(SampleInstruments.NIFTY50, days=20, seed=1)
    assert len(bars) == 20
    assert all(isinstance(bar.close, Decimal) for bar in bars)
    assert all(bar.ts < next_bar.ts for bar, next_bar in pairwise(bars))
    assert all(bar.high >= bar.low for bar in bars)


def test_synthetic_bars_are_seeded_deterministic() -> None:
    first = synthetic_bars(SampleInstruments.NIFTY50, days=10, seed=7)
    second = synthetic_bars(SampleInstruments.NIFTY50, days=10, seed=7)
    assert [bar.close for bar in first] == [bar.close for bar in second]


def test_sma_matches_manual_mean() -> None:
    sma = SMA(3)
    for value in (Decimal(1), Decimal(2), Decimal(3), Decimal(4)):
        sma.update(value)
    assert sma.value == Decimal(3)


def test_backtest_tracks_cash_and_equity() -> None:
    bars = synthetic_bars(SampleInstruments.NIFTY50, days=50, seed=2)
    backtest = Backtest(bars, initial_cash="100000.00")

    def hold_all(_index: int, _bar: object, _position: Decimal) -> Decimal:
        return Decimal("10")

    result = backtest.run(hold_all)
    assert len(result.equity_curve) == len(bars)
    assert result.trades  # final close-out records a round-trip
    assert result.final_equity > Decimal(0)


def test_metrics_report_sane_values() -> None:
    equity = [Decimal(100) + Decimal(i) for i in range(30)]
    metrics = compute_metrics(equity)
    assert metrics.total_return > 0
    assert isinstance(metrics.sharpe, Decimal)
