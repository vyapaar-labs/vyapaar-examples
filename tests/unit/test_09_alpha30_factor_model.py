"""09_alpha30_factor_model regression test."""

from __future__ import annotations


def test_example_09_ranks_universe_and_picks_a_top(load_example) -> None:
    module = load_example("09_alpha30_factor_model")
    result = module.main()
    assert result["universe_size"] == 3
    assert result["top_pick"] in result["ranked"]
    assert result["all_decimal"] is True
    # Ranked symbols are unique and cover the universe.
    assert len(set(result["ranked"])) == result["universe_size"]


def test_example_09_flexible_backtest(load_example) -> None:
    module = load_example("09_alpha30_factor_model")
    res = module.run_backtest(
        initial_cash="1000000.00",
        rebalance_days=15,
        days=60,
    )
    assert res["universe"] == "Alpha30"
    assert res["universe_size"] == 30
    assert res["rebalance_days"] == 15
    assert res["initial_capital"] == "1000000.00"
    assert res["all_decimal"] is True
    assert int(res["total_trades"]) > 0
