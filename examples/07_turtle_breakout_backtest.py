"""07 — Turtle breakout backtest.

Backtests a 20/10-day Donchian-channel turtle on synthetic NIFTY data with the
shared bar-by-bar backtester and reports Sharpe, Sortino, Calmar, max drawdown,
win rate, and expectancy.

Pitfalls::
    - Cost & latency: backtests that ignore brokerage/STT overstate returns on
      high-turnover strategies (turtles trade often).
    - Look-ahead bias: the breakout uses only the *previous* N bars — including
      the current bar's high would leak the fill signal into the entry.
"""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from vyapaar_examples import Backtest, Bar, SampleInstruments, synthetic_bars

ENTRY_PERIOD = 20
EXIT_PERIOD = 10
QUANTITY = Decimal("10")


def main() -> dict[str, object]:
    instrument = SampleInstruments.NIFTY50
    bars = synthetic_bars(instrument, days=300, seed=42)

    backtest = Backtest(bars, initial_cash="1000000.00", costs_per_share="0.05")
    result = backtest.run(_make_turtle_signal())

    metrics = result.metrics
    return {
        "instrument": instrument.value,
        "bars": len(bars),
        "trades": len(result.trades),
        "final_equity": str(result.final_equity),
        "total_return": str(metrics.total_return),
        "sharpe": str(metrics.sharpe),
        "sortino": str(metrics.sortino),
        "calmar": str(metrics.calmar),
        "max_drawdown": str(metrics.max_drawdown),
        "win_rate": str(metrics.win_rate),
        "expectancy": str(metrics.expectancy),
    }


def _make_turtle_signal() -> Callable[[int, Bar, Decimal], Decimal]:
    """Return a fresh Donchian-channel signal (per-run state)."""
    highs: list[Decimal] = []
    lows: list[Decimal] = []

    def signal(index: int, bar: Bar, position: Decimal) -> Decimal:
        del index
        highs.append(bar.high)
        lows.append(bar.low)
        if len(highs) <= ENTRY_PERIOD:
            return position
        channel_high = max(highs[-ENTRY_PERIOD - 1 : -1])
        channel_low = min(lows[-EXIT_PERIOD - 1 : -1])
        if position == 0 and bar.close > channel_high:
            return QUANTITY
        if position > 0 and bar.close < channel_low:
            return Decimal(0)
        return position

    return signal


if __name__ == "__main__":
    print(main())
