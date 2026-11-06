"""01_loading_data regression test."""

from __future__ import annotations


def test_example_01_round_trips_bars(load_example) -> None:
    module = load_example("01_loading_data")
    result = module.main()
    assert result["bars_generated"] == 250
    assert result["rows_reloaded"] == 250
    assert result["monotonic_ts"] is True
    assert result["instrument"] == "NSE:NIFTY50-INDEX"
    assert float(result["last_close"]) > 0
