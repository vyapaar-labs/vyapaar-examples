"""A minimal deterministic bar-by-bar backtester.

A signal function receives the bar index, the bar, and the current position
and returns the *target* quantity. The backtest re-trades to the target at the
bar's close and marks-to-market the equity at every bar. Round-trip PnL is
``(exit - entry) * qty - 2 * costs_per_share * qty``, matching the cash ledger.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from vyapaar_examples._compat import D

# Grafted deterministic engine runs on the mirrored kernel simulator/runner
# (`_kernel.backtest.simulated`, `_kernel.runner`: gap 0006) with the India
# cost/settlement mirror (gap 0004) - deleted when the wheel ships the same.
from vyapaar_examples._kernel.backtest.simulated import (
    FillCostFn as SimFillCostFn,
)
from vyapaar_examples._kernel.backtest.simulated import (
    NextOpenExecution,
    SessionOpen,
    group_sessions,
    make_simulator,
)
from vyapaar_examples._kernel.bar import Bar
from vyapaar_examples._kernel.base import Strategy
from vyapaar_examples._kernel.context import LedgerContext
from vyapaar_examples._kernel.instrument import InstrumentId
from vyapaar_examples._kernel.markets.india.costs import (
    nse_equity_delivery_fill_cost as _kernel_nse_equity_delivery_fill_cost,
)
from vyapaar_examples._kernel.money import Currency, Money
from vyapaar_examples._kernel.order import OrderIntent, OrderSide
from vyapaar_examples._kernel.runner import StrategyRunner
from vyapaar_examples.base import ts_to_date
from vyapaar_examples.data import Bar as FreshBar
from vyapaar_examples.metrics import (
    PerformanceMetrics,
    Trade,
    compute_metrics,
    curve_metrics,
    exposure_metrics,
)

SignalFn = Callable[[int, FreshBar, Decimal], Decimal]


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
        bars: list[FreshBar],
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


# --- deterministic engine graft (run_portfolio_backtest) --------------------
# Verbatim from the honba-harness backtest module (D3: fresh ``backtest.py`` is
# canonical; the engine family below is grafted). ``canonical_hash`` stays the
# fresh definition above (identical body).
INR = Currency.INR

_REJECTION_KIND = {
    "insufficient_funds": "released_unfunded",
    "no_position": "released_no_position",
}


@dataclass(frozen=True, slots=True)
class FillRecord:
    """One fill as the ledger booked it (money in minor units)."""

    date: str
    order_id: str
    symbol: str
    exchange: str
    side: str
    quantity: float
    price: float
    notional_minor: int
    cost_minor: int
    submitted_date: str


@dataclass(frozen=True, slots=True)
class OrderEvent:
    """An order (or part of one) that did not fill, and why."""

    date: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    kind: str  # "suppressed_warmup" | "released_unfunded" | "released_no_position" | ...


def _major(minor: int) -> float:
    return Money.from_minor(minor, INR).to_major()


class CanonicalOrderLedger(LedgerContext):
    """``LedgerContext`` that hands the runner one event's intents in a canonical order.

    A strategy that loops over a ``set`` (Alpha-30 does) emits the same intents in an
    order that depends on ``PYTHONHASHSEED``, which would change order ids, fill order
    and, when cash is short, which buy gets cut. Intents raised by one event are one
    decision, so ordering them (sells first, then by instrument) changes no meaning
    and makes every run reproducible.
    """

    def drain_intents(self) -> list[OrderIntent]:
        return sorted(
            super().drain_intents(),
            key=lambda i: (
                i.side is not OrderSide.SELL,
                i.instrument_id.symbol,
                i.instrument_id.exchange,
            ),
        )


@dataclass
class BacktestRun:
    """Outcome of one run. Money fields are integer minor units; floats are statistics only."""

    capital_minor: int
    settlement_days: int
    fills: list[FillRecord] = field(default_factory=list)
    order_events: list[OrderEvent] = field(default_factory=list)
    curve: list[dict[str, Any]] = field(default_factory=list)
    final_positions: dict[str, float] = field(default_factory=dict)
    fees_minor: int = 0
    traded_notional_minor: int = 0
    warmup_sessions: int = 0
    test_sessions: int = 0
    bars_seen: int = 0
    rejections: int = 0

    def float_curve(self) -> list[dict[str, Any]]:
        """The curve in rupees (floats) for the statistics in ``vyapaar_examples.metrics``."""
        return [
            {
                "date": p["date"],
                "value": _major(p["equity_minor"]),
                "cash": _major(p["cash_minor"]),
            }
            for p in self.curve
        ]

    def metrics(self) -> dict[str, Any]:
        curve = self.float_curve()
        capital = _major(self.capital_minor)
        kinds = [e.kind for e in self.order_events]
        last = self.curve[-1]
        return {
            **curve_metrics(curve, capital),
            **exposure_metrics(curve, _major(self.traded_notional_minor)),
            "final_equity_minor": last["equity_minor"],
            "final_cash_minor": last["cash_minor"],
            "positions_value_minor": last["positions_value_minor"],
            "total_fees_minor": self.fees_minor,
            "total_fees": _major(self.fees_minor),
            "traded_notional_minor": self.traded_notional_minor,
            "n_fills": len(self.fills),
            "n_suppressed_warmup": kinds.count("suppressed_warmup"),
            "n_released_unfunded": kinds.count("released_unfunded"),
            "n_released_no_position": kinds.count("released_no_position"),
            "n_unfilled_at_end": kinds.count("unfilled_at_end"),
            "n_rejected_intents": self.rejections,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "capital_minor": self.capital_minor,
            "settlement_days": self.settlement_days,
            "warmup_sessions": self.warmup_sessions,
            "test_sessions": self.test_sessions,
            "bars_seen": self.bars_seen,
            "metrics": self.metrics(),
            "final_positions": dict(sorted(self.final_positions.items())),
            "fills": [asdict(f) for f in self.fills],
            "order_events": [asdict(e) for e in self.order_events],
            "equity_curve": self.curve,
        }

    def major_metrics(self) -> dict[str, Any]:
        """Metrics in rupees (major units) with readable labels for printing."""
        m = self.metrics()
        out = {k: v for k, v in m.items() if not k.endswith("_minor")}
        out["final_equity"] = _major(m["final_equity_minor"])
        out["final_cash"] = _major(m["final_cash_minor"])
        out["total_fees"] = _major(m["total_fees_minor"])
        out["traded_notional"] = _major(m["traded_notional_minor"])
        out["positions_value"] = _major(m["positions_value_minor"])
        return out


def run_portfolio_backtest(
    strategy: Strategy,
    bars: Sequence[Bar],
    *,
    test_start: dt.date,
    test_end: dt.date,
    capital_minor: int,
    settlement_days: int | None = None,
    costs: SimFillCostFn = _kernel_nse_equity_delivery_fill_cost,
    exchange: str = "NSE",
) -> BacktestRun:
    """Run ``strategy`` over ``bars``; trade and account only within ``[test_start, test_end]``.

    ``settlement_days=None`` takes the core market-pack cycle for ``exchange`` as of
    ``test_start`` (NSE: T+2 before 2023-01-27, T+1 from then); an explicit value wins.
    """
    if test_start > test_end:
        raise ValueError(f"test_start {test_start} is after test_end {test_end}")
    kept = [b for b in bars if ts_to_date(b.ts) <= test_end]
    events = group_sessions(kept)
    session_days = [ts_to_date(e.ts) for e, _ in events if isinstance(e, SessionOpen)]
    if not any(day >= test_start for day in session_days):
        raise ValueError(f"no bars between {test_start} and {test_end}")
    n_warmup = sum(1 for day in session_days if day < test_start)

    port = make_simulator(
        fill="next_open",
        cash=Money.from_minor(capital_minor, INR),
        costs=costs,
        exchange=exchange,
        settlement_days=settlement_days,
        as_of=test_start,
    )
    assert isinstance(port, NextOpenExecution)
    ctx = CanonicalOrderLedger(cash=Money.from_minor(capital_minor, INR))
    runner = StrategyRunner(strategy, port, ctx=ctx, warmup_bars=n_warmup)
    run = BacktestRun(capital_minor=capital_minor, settlement_days=port.settlement_days)
    closes: dict[InstrumentId, float] = {}
    day: dt.date | None = None

    def mark() -> None:
        if day is None or day < test_start:
            return
        positions_value = Money.zero(INR)
        for iid, qty in port.positions.items():
            positions_value = positions_value + Money.mul_qty(qty, closes[iid], INR)
        run.test_sessions += 1
        run.curve.append(
            {
                "date": day.isoformat(),
                "equity_minor": (port.cash + positions_value).amount,
                "cash_minor": port.cash.amount,
                "available_cash_minor": port.available_cash.amount,
                "positions_value_minor": positions_value.amount,
            }
        )

    runner.start()
    for event, ts in events:
        port.on_event(event, ts)
        runner.on_event(event, ts)
        if isinstance(event, SessionOpen):
            mark()
            day = ts_to_date(event.ts)
        elif isinstance(event, Bar):
            closes[event.instrument_id] = event.close
            run.bars_seen += 1
    mark()
    runner.stop()
    run.warmup_sessions = n_warmup

    submitted = {s.order_id: s for s in runner.intents}
    for f in runner.fills:
        notional = Money.mul_qty(f.quantity, f.price, INR).amount
        sub = submitted.get(f.order_id or "")
        run.fills.append(
            FillRecord(
                date=ts_to_date(f.ts).isoformat(),
                order_id=f.order_id or "",
                symbol=f.instrument_id.symbol,
                exchange=f.instrument_id.exchange,
                side=f.side.value,
                quantity=f.quantity,
                price=f.price,
                notional_minor=notional,
                cost_minor=f.costs.amount,
                submitted_date=ts_to_date(sub.ts_init).isoformat() if sub else "",
            )
        )
    timed: list[tuple[int, OrderEvent]] = [
        (s.ts_init, _event(s.ts_init, "", s.intent, s.intent.quantity, "suppressed_warmup"))
        for s in runner.suppressed
    ]
    timed += [
        (
            r.ts,
            _event(
                r.ts,
                r.order_id,
                r.intent,
                r.intent.quantity,
                "cancelled" if r.cancelled else _REJECTION_KIND.get(r.reason, r.reason),
            ),
        )
        for r in runner.order_rejections
    ]
    run.order_events = [e for _, e in sorted(timed, key=lambda t: t[0])]
    last_ts = events[-1][1]
    for order_id in port.working_orders:
        sub = submitted[order_id]
        run.order_events.append(
            _event(last_ts, order_id, sub.intent, sub.intent.quantity, "unfilled_at_end")
        )
    run.fees_minor = port.fees.amount
    run.traded_notional_minor = port.traded_notional.amount
    run.final_positions = {iid.symbol: qty for iid, qty in port.positions.items()}
    run.rejections = len(runner.rejections)
    return run


def _event(ts: int, order_id: str, intent: OrderIntent, qty: float, kind: str) -> OrderEvent:
    return OrderEvent(
        date=ts_to_date(ts).isoformat(),
        order_id=order_id,
        symbol=intent.instrument_id.symbol,
        side=intent.side.value,
        quantity=qty,
        kind=kind,
    )
