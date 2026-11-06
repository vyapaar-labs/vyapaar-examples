"""07_turtle_breakout_backtest regression test."""

from __future__ import annotations

from decimal import Decimal


def test_example_07_backtest_reports_metrics(load_example) -> None:
    module = load_example("07_turtle_breakout_backtest")
    result = module.main()
    assert result["bars"] == 300
    assert result["instrument"] == "NSE:NIFTY50-INDEX"
    assert float(result["final_equity"]) > 0
    assert Decimal(result["total_return"]) != 0
    # Metrics must be exact decimals (strings) that parse cleanly.
    for key in ("sharpe", "sortino", "calmar", "max_drawdown", "win_rate", "expectancy"):
        Decimal(result[key])
