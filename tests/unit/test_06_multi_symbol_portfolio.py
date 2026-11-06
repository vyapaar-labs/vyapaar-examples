"""06_multi_symbol_portfolio regression test."""

from __future__ import annotations


def test_example_06_tracks_multi_symbol_positions(load_example) -> None:
    module = load_example("06_multi_symbol_portfolio")
    result = module.main()
    assert result["all_exact"] is True
    assert len(result["legs"]) == 3
    # Each leg bought 10, sold 4 -> net 6.
    for leg in result["legs"]:
        assert leg["quantity"] == "6"
    # Unrealized PnL is a valid decimal string for every leg.
    for pnl in result["unrealized_pnl"].values():
        float(pnl)  # parseable as a number
