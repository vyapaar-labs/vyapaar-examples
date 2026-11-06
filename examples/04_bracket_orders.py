"""04 — Bracket orders.

Places a parent order with an attached stop-loss and a take-profit target, then
walks the market: the first of the two legs to trigger closes the position.

Pitfalls::
    - Order types: SEBI requires bracket orders to be placed with an exchange
      algorithm; a stop-loss is not guaranteed to fill at your exact trigger —
      gap risk means slippage beyond the stop price.
    - Freeze limits cap the quantity of a single bracket order.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from vyapaar_examples import SampleInstruments, trending_bars

STOP_OFFSET = Decimal("0.05")  # 5% stop distance
TARGET_OFFSET = Decimal("0.10")  # 10% target


@dataclass
class BracketOrder:
    entry_price: Decimal
    quantity: Decimal
    stop: Decimal
    target: Decimal
    status: str = "open"
    exit_price: Decimal | None = None


def main() -> dict[str, object]:
    instrument = SampleInstruments.INFY
    # A 1.1%/day trending series guarantees the target (or stop) leg triggers.
    bars = trending_bars(instrument.value, days=30, base="1800.00", step="20.00")

    entry = bars[0].close
    bracket = BracketOrder(
        entry_price=entry,
        quantity=Decimal("10"),
        stop=entry * (Decimal(1) - STOP_OFFSET),
        target=entry * (Decimal(1) + TARGET_OFFSET),
    )

    for bar in bars[1:]:
        if bracket.status != "open":
            break
        if bar.low <= bracket.stop:
            bracket.status = "stop_hit"
            bracket.exit_price = bracket.stop
        elif bar.high >= bracket.target:
            bracket.status = "target_hit"
            bracket.exit_price = bracket.target

    return {
        "instrument": instrument.value,
        "entry": str(bracket.entry_price),
        "stop": str(bracket.stop),
        "target": str(bracket.target),
        "status": bracket.status,
        "exit_price": str(bracket.exit_price),
    }


if __name__ == "__main__":
    print(main())
