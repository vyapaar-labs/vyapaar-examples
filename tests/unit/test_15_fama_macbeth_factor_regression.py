"""15_fama_macbeth_factor_regression regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_15_fama_macbeth(load_example) -> None:
    module = load_example("15_fama_macbeth_factor_regression")
    result = module.main()
    # T=12, N=8, K=2 — both passes identified.
    assert result["identified"] is True
    assert result["beta_shape"] == [8, 2]
    assert len(result["lambda"]) == 2
    assert len(result["t_stats"]) == 2
    assert result["all_decimal"] is True
    # Mean absolute cross-sectional pricing error is a small positive Decimal.
    assert Decimal(result["mean_abs_alpha"]) > Decimal("0")
