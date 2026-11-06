"""12_portfolio_allocation regression test."""

from __future__ import annotations


def test_example_12_allocation(load_example) -> None:
    module = load_example("12_portfolio_allocation")
    result = module.main()
    assert result["universe_size"] == 3
    assert result["mv_sums_to_one"] is True
    assert result["rp_sums_to_one"] is True
    assert result["bounded_sums_to_one"] is True
    assert result["bounded_respects_cap"] is True
    assert result["bounded_weights_differ"] is True
    assert result["all_decimal"] is True
    # Weights are reported as strings in the wire dict, but computed as Decimal.
    assert all(isinstance(value, str) for value in result["mean_variance_weights"])
