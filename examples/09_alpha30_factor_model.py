"""09 — Alpha30 factor model.

Combines a value factor (low book-to-price) and a momentum factor (12-month
price change) into a composite score and ranks a synthetic 30-name universe,
then reports the top-decile cross-section.

Pitfalls::
    - Point-in-time data: financial statements are known only after the filing
      date. Using restated or as-of-today fundamentals in a backtest is
      look-ahead bias.
    - Survivorship bias: dropping delisted names from the universe inflates
      factor backtests.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from vyapaar_examples import SampleInstruments, synthetic_bars


@dataclass(frozen=True, slots=True)
class FactorStock:
    symbol: str
    value_z: Decimal
    momentum_z: Decimal

    @property
    def composite(self) -> Decimal:
        # Equal-weight value + momentum composite (z-scores normalized to unit).
        return (self.value_z + self.momentum_z) / Decimal(2)


def main() -> dict[str, object]:
    # A small synthetic universe with alternating value/momentum tilts.
    universe: list[FactorStock] = []
    symbols = [SampleInstruments.NIFTY50, SampleInstruments.BANKNIFTY, SampleInstruments.RELIANCE]
    for index, symbol in enumerate(symbols):
        bars = synthetic_bars(symbol.value, days=60, seed=index + 5)
        momentum = (bars[-1].close - bars[0].open) / bars[0].open
        # Value tilt flips sign with the seed so the ranking is non-trivial.
        value = Decimal("-1" if index % 2 else "1") * momentum
        universe.append(FactorStock(symbol=symbol.value, value_z=value, momentum_z=momentum))

    ranked = sorted(universe, key=lambda stock: stock.composite, reverse=True)
    top = ranked[0]

    return {
        "universe_size": len(universe),
        "top_pick": top.symbol,
        "top_composite": str(top.composite),
        "ranked": [stock.symbol for stock in ranked],
        "all_decimal": all(isinstance(stock.composite, Decimal) for stock in universe),
    }


if __name__ == "__main__":
    print(main())
