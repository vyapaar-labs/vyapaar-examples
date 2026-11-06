"""08_nifty_options_microstructure regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_08_options_math_is_exact(load_example) -> None:
    module = load_example("08_nifty_options_microstructure")
    result = module.main()
    assert result["lot_size"] == "75"
    assert result["contract_count"] == 2
    # Premium outlay = 2 legs x 75 lots x 185 premium.
    assert Decimal(result["premium_outlay"]) == Decimal("27750")
    # Straddle break-evens straddle the spot by +/- 370.
    assert Decimal(result["upper_break_even"]) == Decimal("25020.00")
    assert Decimal(result["lower_break_even"]) == Decimal("24280.00")
