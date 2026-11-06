"""06 — Multi-symbol portfolio.

Tracks net positions, average cost, and unrealized PnL across a small universe
(NIFTY50, BANKNIFTY, RELIANCE) as each leg is traded, with exact Decimal
accounting.

Pitfalls::
    - FIFO tax lots: SEBI/ITR tax treatment follows FIFO lots; average-cost
      reporting here is for PnL monitoring only, not tax.
    - Currency/exchange quirks: NFO index products have different lot sizes and
      tick sizes than cash equities — sizes are not fungible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from vyapaar_examples import Bar, SampleInstruments, synthetic_bars

INSTRUMENTS = [SampleInstruments.NIFTY50, SampleInstruments.BANKNIFTY, SampleInstruments.RELIANCE]


@dataclass
class LegPosition:
    instrument: str
    quantity: Decimal = field(default_factory=lambda: Decimal(0))
    average_price: Decimal = field(default_factory=lambda: Decimal(0))

    def apply_fill(self, side: str, quantity: Decimal, price: Decimal) -> None:
        signed = quantity if side == "buy" else -quantity
        new_quantity = self.quantity + signed
        if new_quantity == 0:
            self.average_price = Decimal(0)
        elif self.quantity == 0 or (self.quantity > 0) != (new_quantity > 0):
            self.average_price = price
        self.quantity = new_quantity


def main() -> dict[str, object]:
    universes: dict[str, list[Bar]] = {}
    for index, instrument in enumerate(INSTRUMENTS):
        universes[instrument.value] = synthetic_bars(
            instrument.value,
            days=60,
            seed=index + 1,
            base_price_paise=24_000 * (index + 1),
        )

    positions = {instrument.value: LegPosition(instrument.value) for instrument in INSTRUMENTS}
    # Trade each leg once: buy 10 on day 5, sell 4 on day 25.
    for instrument in INSTRUMENTS:
        bars = universes[instrument.value]
        positions[instrument.value].apply_fill("buy", Decimal("10"), bars[5].close)
        positions[instrument.value].apply_fill("sell", Decimal("4"), bars[25].close)

    unrealized = {
        instrument.value: positions[instrument.value].quantity
        * (universes[instrument.value][-1].close - positions[instrument.value].average_price)
        for instrument in INSTRUMENTS
    }

    return {
        "legs": [
            {
                "instrument": position.instrument,
                "quantity": str(position.quantity),
                "average_price": str(position.average_price),
            }
            for position in positions.values()
        ],
        "unrealized_pnl": {key: str(value) for key, value in unrealized.items()},
        "all_exact": all(
            isinstance(position.quantity, Decimal) and isinstance(position.average_price, Decimal)
            for position in positions.values()
        ),
    }


if __name__ == "__main__":
    print(main())
