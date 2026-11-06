"""14_timeseries_forecast regression test."""

from __future__ import annotations


def test_example_14_forecast(load_example) -> None:
    module = load_example("14_timeseries_forecast")
    result = module.main()
    assert result["horizon"] == 10
    assert len(result["point_forecast"]) == result["horizon"]
    assert len(result["interval_lower"]) == result["horizon"]
    assert len(result["interval_upper"]) == result["horizon"]
    assert result["interval_contains_point"] is True
    assert result["all_decimal"] is True
    assert result["observations"] >= 3
