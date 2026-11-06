"""10 — Walk-forward optimization.

Runs a walk-forward optimizer that picks the SMA-lookback with the best
Sharpe-like objective on each training window and evaluates it on the next
validation window, then reports per-window stability.

Pitfalls::
    - Overfitting: optimizing on the full sample (rather than rolling
      train/validate windows) selects parameters that fit noise.
    - WFO still needs realistic costs: parameter sets that look great on gross
      returns can be net losers after STT + brokerage.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from vyapaar_examples import (
    Backtest,
    SampleInstruments,
    synthetic_bars,
    walk_forward_optimize,
)


def _sharpe_objective(bars: list[Any], params: dict[str, Any]) -> float:
    """Return the backtest Sharpe for a given SMA lookback (as a float score)."""
    lookback = int(params["lookback"])
    backtest = Backtest(bars, initial_cash="500000.00")
    result = backtest.run(_make_sma_signal(lookback))
    return float(result.metrics.sharpe)


def _make_sma_signal(lookback: int) -> Any:
    from vyapaar_examples import SMA

    sma = SMA(lookback)

    def signal(index: int, bar: Any, position: Decimal) -> Decimal:
        del index
        sma.update(bar.close)
        if not sma.ready:
            return position
        if position == 0 and bar.close < sma.value:
            return Decimal("10")
        if position > 0 and bar.close > sma.value:
            return Decimal(0)
        return position

    return signal


def main() -> dict[str, object]:
    instrument = SampleInstruments.BANKNIFTY
    bars = synthetic_bars(instrument.value, days=240, seed=17)

    param_grid = [{"lookback": lookback} for lookback in (5, 10, 20)]
    results = walk_forward_optimize(
        bars,
        param_grid=param_grid,
        objective_fn=_sharpe_objective,
        train_size=120,
        validate_size=40,
    )

    return {
        "instrument": instrument.value,
        "windows": len(results),
        "chosen_params": [window.params for window in results],
        "train_objectives": [window.train_objective for window in results],
        "validate_objectives": [window.validate_objective for window in results],
        "stable": all(result.params == results[0].params for result in results),
    }


if __name__ == "__main__":
    print(main())
