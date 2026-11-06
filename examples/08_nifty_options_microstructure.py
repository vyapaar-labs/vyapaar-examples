"""08 — NFO options microstructure.

Walks through NFO weekly-option mechanics: lot size, strike step, premium, and
the ATM straddle break-even — all in exact Decimal.

Pitfalls::
    - Options expire weekly; theta decays fast and most OTM options go to zero —
      a long premium is not "cheap" near expiry.
    - Strike steps and lot sizes differ per underlying; margin/freeze limits
      treat options contracts (not shares) as the trading unit.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

LOT_SIZE = Decimal("75")  # NIFTY weekly lot
STRIKE_STEP = Decimal("50")  # NIFTY strike step
PREMIUM = Decimal("185.00")
SPOT = Decimal("24650.00")


@dataclass(frozen=True, slots=True)
class OptionLeg:
    kind: str
    strike: Decimal
    premium: Decimal
    lots: int

    @property
    def contract_value(self) -> Decimal:
        return self.premium * LOT_SIZE * Decimal(self.lots)


def main() -> dict[str, object]:
    # Two ATM strikes around the spot, one lot each.
    atm_strike = (SPOT // STRIKE_STEP) * STRIKE_STEP
    call = OptionLeg("CE", atm_strike, PREMIUM, 1)
    put = OptionLeg("PE", atm_strike, PREMIUM, 1)

    premium_outlay = call.contract_value + put.contract_value
    # Straddle break-even = spot +/- total premium per share.
    total_premium_per_share = PREMIUM + PREMIUM
    upper_break_even = SPOT + total_premium_per_share
    lower_break_even = SPOT - total_premium_per_share

    return {
        "spot": str(SPOT),
        "atm_strike": str(atm_strike),
        "lot_size": str(LOT_SIZE),
        "strike_step": str(STRIKE_STEP),
        "premium_outlay": str(premium_outlay),
        "upper_break_even": str(upper_break_even),
        "lower_break_even": str(lower_break_even),
        "contract_count": 2,
    }


if __name__ == "__main__":
    print(main())
