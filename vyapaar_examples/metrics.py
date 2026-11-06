"""Performance metrics: exact ``Decimal`` equity and trade statistics.

Statistical ratios (Sharpe/Sortino/Calmar) are dimensionless but are still
computed with ``Decimal`` (``Decimal.sqrt``) to keep every numeric output exact
and free of binary floating point.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from vyapaar_examples._compat import D

ANNUALIZATION = Decimal(252)


@dataclass(frozen=True, slots=True)
class Trade:
    """A closed round-trip with exact PnL."""

    instrument: str
    entry_ts: datetime
    exit_ts: datetime
    quantity: Decimal
    entry_price: Decimal
    exit_price: Decimal
    pnl: Decimal


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    """Summarized backtest statistics."""

    total_return: Decimal
    annualized_return: Decimal
    sharpe: Decimal
    sortino: Decimal
    calmar: Decimal
    max_drawdown: Decimal
    win_rate: Decimal
    expectancy: Decimal


def compute_metrics(
    equity_curve: list[Decimal],
    trades: list[Trade] | None = None,
) -> PerformanceMetrics:
    """Compute metrics from an equity curve (and optional closed trades)."""
    if len(equity_curve) < 2:
        raise ValueError("equity curve needs at least two points")

    returns = _returns(equity_curve)
    total_return = equity_curve[-1] / equity_curve[0] - D(1)
    years = D(len(equity_curve)) / ANNUALIZATION
    annualized_return = (
        (equity_curve[-1] / equity_curve[0]) ** (D(1) / years) - D(1) if years > 0 else D(0)
    )
    max_drawdown = _max_drawdown(equity_curve)

    mean = sum(returns, D(0)) / D(len(returns))
    std = _stddev(returns)
    sharpe = (mean / std * ANNUALIZATION.sqrt()) if std > 0 else D(0)

    downside = [r for r in returns if r < 0]
    downside_std = _stddev(downside) if downside else D(0)
    sortino = (mean / downside_std * ANNUALIZATION.sqrt()) if downside_std > 0 else D(0)

    calmar = (annualized_return / abs(max_drawdown)) if max_drawdown != 0 else D(0)

    if trades:
        pnls = [trade.pnl for trade in trades]
        wins = [pnl for pnl in pnls if pnl > 0]
        win_rate = D(len(wins)) / D(len(pnls)) if pnls else D(0)
        expectancy = sum(pnls, D(0)) / D(len(pnls)) if pnls else D(0)
    else:
        win_rate = D(0)
        expectancy = D(0)

    return PerformanceMetrics(
        total_return=total_return,
        annualized_return=annualized_return,
        sharpe=sharpe,
        sortino=sortino,
        calmar=calmar,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
        expectancy=expectancy,
    )


def _returns(equity_curve: list[Decimal]) -> list[Decimal]:
    return [equity_curve[i] / equity_curve[i - 1] - D(1) for i in range(1, len(equity_curve))]


def _stddev(values: list[Decimal]) -> Decimal:
    mean = sum(values, D(0)) / D(len(values))
    variance = sum((value - mean) ** 2 for value in values) / D(len(values))
    return variance.sqrt()


def _max_drawdown(equity_curve: list[Decimal]) -> Decimal:
    peak = equity_curve[0]
    max_drawdown = D(0)
    for value in equity_curve[1:]:
        if value > peak:
            peak = value
        drawdown = (value - peak) / peak if peak != 0 else D(0)
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    return max_drawdown
