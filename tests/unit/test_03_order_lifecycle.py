"""03_order_lifecycle regression test."""

from __future__ import annotations


def test_example_03_market_fills_and_limit_rests_then_fills(load_example) -> None:
    module = load_example("03_order_lifecycle")
    result = module.main()
    assert result["market_status"] == "complete"
    assert float(result["market_fill_price"]) > 0
    assert result["limit_status"] == "complete"
    assert float(result["limit_fill_price"]) > 0
    assert result["fills_are_decimal"] is True
