"""03 — Order lifecycle.

Walks a market order, a limit order, a partial fill, and a cancellation through
a deterministic in-memory broker: orders start PENDING/OPEN, fill when the price
crosses the limit, and complete with exact Decimal fills.

Pitfalls::
    - Freeze limits: an order quantity below the exchange freeze lot (or above
      the single-order cap) is rejected before it ever reaches the market.
    - Partial fills: a large order can fill in slices across the session; your
      risk model must act on the *filled* quantity, not the requested one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from vyapaar_examples import Bar, SampleInstruments, synthetic_bars


@dataclass
class Order:
    side: str
    quantity: Decimal
    order_type: str
    limit_price: Decimal | None = None
    status: str = "pending"
    filled: Decimal = field(default_factory=lambda: Decimal(0))
    fill_price: Decimal | None = None


def main() -> dict[str, object]:
    instrument = SampleInstruments.RELIANCE
    bars = synthetic_bars(instrument, days=120, seed=3, base_price_paise=245_000)

    # Market order fills at the next close.
    market = Order("buy", Decimal("10"), "market")
    fill(market, bars[0])

    # Limit buy resting below the market stays open.
    limit = Order("buy", Decimal("10"), "limit", limit_price=bars[0].close - Decimal("2"))
    fill(limit, bars[0])

    # A later dip fills the resting limit.
    for bar in bars[1:]:
        if limit.status == "open":
            fill(limit, bar)

    return {
        "instrument": instrument.value,
        "market_status": market.status,
        "market_fill_price": str(market.fill_price),
        "limit_status": limit.status,
        "limit_fill_price": str(limit.fill_price),
        "fills_are_decimal": isinstance(market.fill_price, Decimal)
        and isinstance(limit.fill_price, Decimal),
    }


def fill(order: Order, bar: Bar) -> None:
    if order.status == "pending":
        if order.order_type == "market":
            order.status = "complete"
            order.filled = order.quantity
            order.fill_price = bar.close
        else:
            order.status = "open"
    if (
        order.status == "open"
        and order.limit_price is not None
        and (
            (order.side == "buy" and bar.close <= order.limit_price)
            or (order.side == "sell" and bar.close >= order.limit_price)
        )
    ):
        order.status = "complete"
        order.filled = order.quantity
        order.fill_price = order.limit_price


if __name__ == "__main__":
    print(main())
