"""02_indicators regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_02_computes_exact_indicators(load_example) -> None:
    module = load_example("02_indicators")
    result = module.main()
    assert result["all_decimal"] is True
    assert result["bars"] == 120
    # SMA(20) of a positive price series must be positive.
    assert Decimal(result["sma20"]) > 0
    assert Decimal("0") <= Decimal(result["rsi14"]) <= Decimal("100")
    assert result["fast_crosses"] >= 0
