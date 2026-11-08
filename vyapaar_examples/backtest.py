"""A minimal deterministic bar-by-bar backtester.

A signal function receives the bar index, the bar, and the current position
and returns the *target* quantity. The backtest re-trades to the target at the
bar's close and marks-to-market the equity at every bar. Round-trip PnL is
``(exit - entry) * qty - 2 * costs_per_share * qty``, matching the cash ledger.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from vyapaar_examples._compat import D
from vyapaar_examples._kernel.order import OrderSide
from vyapaar_examples.data import Bar
from vyapaar_examples.metrics import PerformanceMetrics, Trade, compute_metrics

SignalFn = Callable[[int, Bar, Decimal], Decimal]


@dataclass(frozen=True, slots=True)
class BacktestResult:
    """Outcome of a backtest run."""

    equity_curve: list[Decimal]
    trades: list[Trade]
    metrics: PerformanceMetrics
    final_equity: Decimal


class Backtest:
    """Zero-friction, zero-float backtester for the learning path."""

    def __init__(
        self,
        bars: list[Bar],
        initial_cash: Decimal | str = "100000.00",
        costs_per_share: Decimal | str = "0.00",
    ) -> None:
        if not bars:
            raise ValueError("bars must not be empty")
        self.bars = bars
        self.initial_cash = (
            initial_cash if isinstance(initial_cash, Decimal) else Decimal(str(initial_cash))
        )
        self.costs_per_share = (
            costs_per_share
            if isinstance(costs_per_share, Decimal)
            else Decimal(str(costs_per_share))
        )

    def run(self, signal_fn: SignalFn) -> BacktestResult:
        cash = self.initial_cash
        position = D(0)
        entry_price: Decimal | None = None
        entry_ts: datetime | None = None
        equity_curve: list[Decimal] = []
        trades: list[Trade] = []

        for index, bar in enumerate(self.bars):
            target = signal_fn(index, bar, position)
            if target != position:
                if position != 0 and entry_price is not None and entry_ts is not None:
                    pnl = (bar.close - entry_price) * position - self.costs_per_share * abs(
                        position
                    ) * 2
                    trades.append(
                        Trade(
                            instrument=bar.instrument,
                            entry_ts=entry_ts,
                            exit_ts=bar.ts,
                            quantity=abs(position),
                            entry_price=entry_price,
                            exit_price=bar.close,
                            pnl=pnl,
                        )
                    )
                delta = target - position
                cash -= delta * bar.close + abs(delta) * self.costs_per_share
                position = target
                if position != 0:
                    entry_price = bar.close
                    entry_ts = bar.ts
                else:
                    entry_price = None
                    entry_ts = None
            equity_curve.append(cash + position * bar.close)

        final = self.bars[-1]
        if position != 0 and entry_price is not None and entry_ts is not None:
            pnl = (final.close - entry_price) * position - self.costs_per_share * abs(position) * 2
            trades.append(
                Trade(
                    instrument=final.instrument,
                    entry_ts=entry_ts,
                    exit_ts=final.ts,
                    quantity=abs(position),
                    entry_price=entry_price,
                    exit_price=final.close,
                    pnl=pnl,
                )
            )
            cash += position * final.close
            position = D(0)
            equity_curve[-1] = cash

        metrics = compute_metrics(equity_curve, trades)
        return BacktestResult(
            equity_curve=equity_curve,
            trades=trades,
            metrics=metrics,
            final_equity=equity_curve[-1],
        )


# ---------------------------------------------------------------------------
# Stage-1 grafts from the harness backtest module (staged port, plan 0002)
# ---------------------------------------------------------------------------
FillCostFn = Callable[[OrderSide, Decimal, Decimal], Decimal]
"""Simulator fill-cost contract: ``(side, quantity, price) -> cost``; cost in INR Decimal."""


def canonical_hash(payload: Any) -> str:
    """sha256 of the canonical (sorted-key, compact) JSON form of ``payload``."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# India equity-delivery (CNC) rates transcribed exactly from the kernel cost pack
# (markets.india.costs, 2025-26 discount-broker schedule).
_PAISE = Decimal("0.01")
_EQ_DEL_STT_SELL = Decimal("0.0010")
_EQ_DEL_STAMP_BUY = Decimal("0.00015")
_EQ_DEL_EXCH = Decimal("0.0000297")
_EQ_DEL_SEBI = Decimal("0.000001")
_EQ_DEL_IPFT = Decimal("0.000001")
_EQ_DEL_BROKERAGE_PCT = Decimal("0.0003")
_EQ_DEL_BROKERAGE_CAP = Decimal("20")
_GST_RATE = Decimal("0.18")


def _is_buy(side: OrderSide | str) -> bool:
    return str(getattr(side, "value", side)).upper().endswith("BUY")


def nse_equity_delivery_fill_cost(side: OrderSide, quantity: Decimal, price: Decimal) -> Decimal:
    """NSE equity-delivery (CNC) cost of one fill as exact Decimal.

    Each leg is rounded to the paisa once, then legs sum (matching the kernel cost
    pack's fill-cost function). Statutory legs: STT on sell only, stamp duty on buy
    only, GST on the taxable legs. Second-arg/3rd-arg also accept strings/ints via
    ``Decimal(str(...))`` so callers never need floats.
    """
    qty = quantity if isinstance(quantity, Decimal) else Decimal(str(quantity))
    px = price if isinstance(price, Decimal) else Decimal(str(price))
    notional = abs(qty * px)
    if notional <= 0:
        return _PAISE
    brokerage = min(_EQ_DEL_BROKERAGE_PCT * notional, _EQ_DEL_BROKERAGE_CAP)
    legs = (
        brokerage,
        _PAISE if _is_buy(side) else _EQ_DEL_STT_SELL * notional,
        _EQ_DEL_EXCH * notional,
        _EQ_DEL_SEBI * notional,
        _EQ_DEL_IPFT * notional,
        _EQ_DEL_STAMP_BUY * notional if _is_buy(side) else _PAISE,
        _GST_RATE * (brokerage + (_EQ_DEL_EXCH + _EQ_DEL_SEBI + _EQ_DEL_IPFT) * notional),
    )
    total = _PAISE
    for leg in legs:
        total += leg.quantize(_PAISE)
    return total
