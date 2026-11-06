"""02 — Indicators.

Computes a 20-day SMA and a 14-day RSI over a synthetic NIFTY series using
exact Decimal arithmetic, and reports the latest values plus the final SMA cross.

Pitfalls::
    - Indicator warm-up: SMA/RSI are undefined until the window fills; trading
      before ``ready`` uses meaningless values.
    - Float decay: RSI/EMA smoothing must stay in exact Decimal; a float in the
      smoothing path silently corrupts precision over long histories.
"""

from __future__ import annotations

from decimal import Decimal

from vyapaar_examples import RSI, SMA, SampleInstruments, synthetic_bars


def main() -> dict[str, object]:
    instrument = SampleInstruments.NIFTY50
    bars = synthetic_bars(instrument, days=120, seed=7, base_price_paise=24_000)

    fast = SMA(10)
    slow = SMA(20)
    rsi = RSI(14)
    crosses = 0
    for bar in bars:
        fast.update(bar.close)
        slow.update(bar.close)
        rsi.update(bar.close)
        if _crossed_above(fast, slow):
            crosses += 1

    return {
        "instrument": instrument.value,
        "bars": len(bars),
        "sma20": str(slow.value),
        "rsi14": str(rsi.value),
        "fast_crosses": crosses,
        "all_decimal": isinstance(slow.value, Decimal) and isinstance(rsi.value, Decimal),
    }


def _crossed_above(fast: SMA, slow: SMA) -> bool:
    fast_prev = fast.previous_value
    slow_prev = slow.previous_value
    return bool(
        fast_prev is not None
        and slow_prev is not None
        and fast_prev <= slow_prev
        and fast.value > slow.value
    )


if __name__ == "__main__":
    print(main())
