"""11 — Autonomous research loop.

Runs a mini research loop that iteratively asks a (scripted) LLM for a
strategy hypothesis, backtests it, and feeds the outcome back until the budget
is exhausted — deterministic offline thanks to ``ScriptedFakeLlm``.

Pitfalls::
    - Untrusted AI: an AI agent's orders must pass the risk gate before
      execution; a "clever" LLM suggestion is still just a signal.
    - Replayability: prompts, seeds, and temperatures must be archived so any
      research decision can be reproduced exactly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from vyapaar_examples import (
    Backtest,
    SampleInstruments,
    ScriptedFakeLlm,
    synthetic_bars,
)

BUDGET = 3


def main() -> dict[str, object]:
    instrument = SampleInstruments.RELIANCE
    bars = synthetic_bars(instrument.value, days=120, seed=9)

    llm = ScriptedFakeLlm(
        [
            "Buy on a dip below the 20-bar average and exit at the average.",
            "Extend the dip threshold to two standard deviations.",
            "Reduce position size on the third iteration.",
        ]
    )

    iterations: list[dict[str, object]] = []
    for step in range(BUDGET):
        hypothesis = llm.ask("Given the price series, propose a trading rule.")
        backtest = Backtest(bars, initial_cash="500000.00", costs_per_share="0.05")
        result = backtest.run(_make_dip_signal(threshold=Decimal(step + 1)))
        iterations.append(
            {
                "step": step,
                "hypothesis": hypothesis,
                "trades": len(result.trades),
                "total_return": str(result.metrics.total_return),
            }
        )

    return {
        "instrument": instrument.value,
        "iterations": iterations,
        "prompts_seen": len(llm.prompts),
        "deterministic": True,
    }


def _make_dip_signal(threshold: Decimal) -> Any:
    from vyapaar_examples import SMA

    sma = SMA(20)

    def signal(index: int, bar: Any, position: Decimal) -> Decimal:
        del index
        sma.update(bar.close)
        if not sma.ready:
            return position
        if position == 0 and bar.close < sma.value - threshold * Decimal("0.01") * sma.value:
            return Decimal("10")
        if position > 0 and bar.close >= sma.value:
            return Decimal(0)
        return position

    return signal


if __name__ == "__main__":
    print(main())
