"""05 — Partial fills.

Simulates a large limit order filling in slices across several bars: each bar
fills the portion of the order the crossed volume allows, demonstrating
PARTIALLY_FILLED state tracking.

Pitfalls::
    - STT and brokerage are charged on the *executed* quantity; a partially
      filled order still incurs costs immediately on the filled slice.
    - IOC orders cancel the unfilled remainder instantly — never assume a full
      fill for large marketable quantities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from vyapaar_examples import SampleInstruments, synthetic_bars


@dataclass
class SlicedOrder:
    quantity: Decimal
    limit_price: Decimal
    filled: Decimal = field(default_factory=lambda: Decimal(0))
    status: str = "open"


def main() -> dict[str, object]:
    instrument = SampleInstruments.TCS
    bars = synthetic_bars(instrument, days=120, seed=21, base_price_paise=420_000)

    # A 100-share buy with a limit slightly below the market; 20 shares fill per
    # bar whenever the close crosses the limit.
    order = SlicedOrder(quantity=Decimal("100"), limit_price=bars[0].close - Decimal("5"))
    slice_size = Decimal("20")

    for bar in bars[1:]:
        if order.status != "open":
            break
        if bar.close <= order.limit_price:
            order.filled += slice_size
            if order.filled >= order.quantity:
                order.filled = order.quantity
                order.status = "complete"

    return {
        "instrument": instrument.value,
        "requested": str(order.quantity),
        "filled": str(order.filled),
        "status": order.status,
        "remaining": str(order.quantity - order.filled),
        "completed": order.status == "complete",
    }


if __name__ == "__main__":
    print(main())
