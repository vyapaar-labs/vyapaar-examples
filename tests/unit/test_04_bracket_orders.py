"""04_bracket_orders regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_04_trending_series_hits_a_bracket_leg(load_example) -> None:
    module = load_example("04_bracket_orders")
    result = module.main()
    assert result["status"] in ("stop_hit", "target_hit")
    assert float(result["exit_price"]) > 0
    assert Decimal(result["stop"]) < Decimal(result["entry"]) < Decimal(result["target"])
