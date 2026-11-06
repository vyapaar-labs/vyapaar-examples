"""13_black_scholes_greeks regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_13_pricing(load_example) -> None:
    module = load_example("13_black_scholes_greeks")
    result = module.main()
    assert result["all_decimal"] is True
    assert result["call_gt_put"] is True
    assert result["delta_call_positive"] is True
    assert result["delta_put_negative"] is True
    assert result["gamma_positive"] is True
    assert result["iv_recovered"] is True
    # At-the-money call with 20% vol and 30 days to expiry costs a few hundred paise.
    assert Decimal(result["call"]["price"]) > Decimal("0")
    assert Decimal(result["put"]["price"]) > Decimal("0")
