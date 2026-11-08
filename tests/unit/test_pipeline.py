"""tests/unit/test_pipeline.py: Unit tests for the composable pipeline DSL (Phase 3)."""

from __future__ import annotations

import datetime as dt

import pytest

from vyapaar_examples.pipeline import (
    BreakoutSignal,
    BuyAndHoldSignal,
    DividendYieldScreener,
    EqualWeightSizer,
    FixedSipSizer,
    FundamentalQualityFilter,
    InverseVolatilitySizer,
    LiquidityFilter,
    MarketRegimeFilter,
    MultibaggerScreener,
    Pipeline,
    SipBacktestHarness,
    Step,
    ValueScreener,
    parse_symbols,
)
from vyapaar_examples.pipeline.base import PipelineResult


class _RecordStep(Step):
    """Test step that records a value onto the context."""

    def __init__(self, name: str, key: str, value: object) -> None:
        self.name = name
        self.key = key
        self.value = value

    def run(self, ctx: dict) -> dict:
        ctx[self.key] = self.value
        return ctx


def test_operator_overload_chains_into_pipeline() -> None:
    a = _RecordStep("a", "a", 1)
    b = _RecordStep("b", "b", 2)

    pipeline = a >> b
    assert isinstance(pipeline, Pipeline)
    assert [s.name for s in pipeline.steps] == ["a", "b"]

    piped = a | b
    assert isinstance(piped, Pipeline)
    assert len(piped) == 2

    chained = a >> b >> _RecordStep("c", "c", 3)
    assert [s.name for s in chained.steps] == ["a", "b", "c"]

    nested = Pipeline([a]) >> Pipeline([b])
    assert [s.name for s in nested.steps] == ["a", "b"]


def test_pipeline_run_flows_context() -> None:
    pipeline = _RecordStep("a", "a", 1) >> _RecordStep("b", "b", 2)
    result = pipeline.run()
    assert isinstance(result, PipelineResult)
    assert result["a"] == 1 and result["b"] == 2
    assert pipeline.run({"a": 99})["a"] == 1
    assert pipeline.append(_RecordStep("c", "c", 3)).run()["c"] == 3


def test_multibagger_screener_returns_candidates(catalog_dir, add_series) -> None:
    # A monotonic rising series satisfies the trend template at a mid-history asof:
    # close >= sma50 >= rising sma200, within 15% of high52, 1y return >= 15%. The
    # fundamentals DB stays absent, so the leverage gate is skipped (as in source).
    add_series("RELIANCE", closes=[100.0 + i for i in range(800)])
    result = MultibaggerScreener(asof="2024-01-01", top=3, catalog_dir=catalog_dir).run({})
    assert result["symbols"]
    assert len(result["symbols"]) <= 3
    assert result["candidates"][0]["symbol"] in result["symbols"]
    assert result["candidates"][0]["close"] > 0


def test_value_and_dividend_screeners_produce_symbols(catalog_dir, add_series) -> None:
    # A rising series sits far above the 52-week low, so both screens yield an
    # empty candidate set and the run only has to not raise.
    add_series("TCS", closes=[100.0 + i for i in range(300)])
    value = ValueScreener(
        asof="2025-03-01", max_pe=20.0, max_pb=2.0, top=3, catalog_dir=catalog_dir
    ).run({})
    assert all(c["pe_ratio"] is None or c["pe_ratio"] <= 20.0 for c in value["candidates"])

    dividend = DividendYieldScreener(
        asof="2025-03-01", min_yield_pct=3.0, top=3, catalog_dir=catalog_dir
    ).run({})
    assert all(c["div_yield_pct"] >= 3.0 for c in dividend["candidates"])


def test_fundamental_quality_filter_filters_by_roce() -> None:
    ctx = {
        "candidates": [
            {
                "symbol": "PASS",
                "roce_pct": 18.0,
                "debt_to_equity": 0.4,
                "operating_margin_pct": 12.0,
            },
            {"symbol": "LOW_ROCE", "roce_pct": 8.0, "debt_to_equity": 0.4},
            {"symbol": "LEVERED", "roce_pct": 25.0, "debt_to_equity": 2.0},
            {"symbol": "THIN_MARGIN", "roce_pct": 25.0, "operating_margin_pct": -1.0},
            {"symbol": "UNKNOWN", "roce_pct": None, "debt_to_equity": None},
        ],
        "symbols": ["PASS", "LOW_ROCE", "LEVERED", "THIN_MARGIN", "UNKNOWN"],
    }
    result = FundamentalQualityFilter(
        min_roce=15.0, max_debt_to_equity=1.0, min_operating_margin=0.0
    ).run(ctx)
    # UNKNOWN (missing ROCE/debt) now fails the gate; THIN_MARGIN lacks debt/equity
    assert result["symbols"] == ["PASS"]


def test_market_regime_filter_passes_and_blocks(catalog_dir, add_series) -> None:
    # Rising RELIANCE bars put the close above its SMA200; NIFTY stays absent so the
    # benchmark-missing pass-through path is exercised on the same catalog.
    add_series("RELIANCE", closes=[100.0 + i for i in range(300)])
    ctx = {
        "symbols": ["RELIANCE", "TCS"],
        "candidates": [{"symbol": "RELIANCE"}, {"symbol": "TCS"}],
        "asof": dt.date(2024, 6, 3),
    }
    bullish = MarketRegimeFilter(
        benchmark="RELIANCE", condition="above_sma200", catalog_dir=catalog_dir
    ).run(dict(ctx))
    bearish = MarketRegimeFilter(
        benchmark="RELIANCE", condition="below_sma200", catalog_dir=catalog_dir
    ).run(dict(ctx))
    assert bullish["regime"]["above_sma"] is True
    assert bullish["symbols"] == ["RELIANCE", "TCS"]
    assert bearish["symbols"] == []
    assert bearish["candidates"] == []

    missing = MarketRegimeFilter(benchmark="NIFTY", catalog_dir=catalog_dir).run(dict(ctx))
    assert missing["symbols"] == ["RELIANCE", "TCS"]
    assert "not found" in missing["regime"]["reason"]


def test_liquidity_filter_thresholds(catalog_dir, add_series) -> None:
    # Fixture volume (1e6) keeps every symbol above the zero floor but far under 1e18.
    add_series("RELIANCE", closes=[200.0 + i for i in range(60)])
    add_series("TCS", closes=[300.0 + i for i in range(60)])
    ctx = {
        "symbols": ["RELIANCE", "TCS"],
        "candidates": [{"symbol": "RELIANCE"}, {"symbol": "TCS"}],
        "asof": dt.date(2024, 6, 3),
    }
    assert LiquidityFilter(min_avg_turnover=0.0, catalog_dir=catalog_dir).run(dict(ctx))[
        "symbols"
    ] == ["RELIANCE", "TCS"]
    assert (
        LiquidityFilter(min_avg_turnover=1e18, catalog_dir=catalog_dir).run(dict(ctx))["symbols"]
        == []
    )


def test_sizers_produce_weights_summing_to_one(catalog_dir, add_series) -> None:
    # The volatility sizer reads the catalog; the other two sizers avoid data entirely.
    add_series("RELIANCE", closes=[200.0 + i for i in range(60)])
    add_series("TCS", closes=[300.0 + 2 * i for i in range(60)])
    ctx = {"symbols": ["AAA", "BBB", "CCC"]}
    for sizer in (FixedSipSizer(monthly_amount=10000.0), EqualWeightSizer()):
        weights = sizer.run(dict(ctx))["weights"]
        assert set(weights) == {"AAA", "BBB", "CCC"}
        assert sum(weights.values()) == pytest.approx(1.0)

    fixed = FixedSipSizer(monthly_amount=5000.0).run(dict(ctx))
    assert fixed["monthly_amount"] == 5000.0

    vol_ctx = {"symbols": ["RELIANCE", "TCS"], "asof": dt.date(2024, 6, 3)}
    vol_weights = InverseVolatilitySizer(catalog_dir=catalog_dir).run(vol_ctx)["weights"]
    assert sum(vol_weights.values()) == pytest.approx(1.0)


def test_signal_stubs_are_pass_through() -> None:
    ctx = {"symbols": ["RELIANCE"], "candidates": [{"symbol": "RELIANCE"}]}
    assert BuyAndHoldSignal().run(dict(ctx))["signal"] == "buy_and_hold"
    breakout = BreakoutSignal(lookback=10).run(dict(ctx))
    assert breakout["signal"] == "breakout"
    assert breakout["symbols"] == ["RELIANCE"]


def test_end_to_end_pipeline_returns_summary(catalog_dir, add_series, data_env, fund) -> None:
    # Rising bars end at SCREEN_ASOF, so the multibaggier asof (2024-01-01) sees 600+
    # prior sessions and the SIP window fills the catalog tail through 2024-06. The
    # fundamentals row satisfies both the screener's leverage gate and the quality
    # filter's ROCE gate (a missing ROCE would drop the candidate).
    add_series("RELIANCE", closes=[100.0 + i for i in range(800)])
    fund.ratio("RELIANCE", dt.date(2023, 6, 30), roce_pct=18.0, debt_to_equity=0.4)
    pipeline = (
        MultibaggerScreener(asof="2024-01-01", top=3, catalog_dir=catalog_dir)
        >> FundamentalQualityFilter(min_roce=0.0, max_debt_to_equity=5.0)
        >> FixedSipSizer(monthly_amount=10000.0)
        >> SipBacktestHarness(asof="2024-01-01", end_date="2025-01-01", catalog_dir=catalog_dir)
    )
    assert isinstance(pipeline, Pipeline)
    results = pipeline.run()
    assert results.summary is not None
    assert results.summary["candidate_count"] > 0
    assert results.summary["total_invested"] > 0
    assert results.stocks
    assert results.weights
    results.print_summary()


def test_parse_symbols_matches_cli_stream_contract() -> None:
    assert parse_symbols("") == []
    assert parse_symbols("tcs, infy ,reliance") == ["TCS", "INFY", "RELIANCE"]
    assert parse_symbols('{"candidates": [{"symbol": "tcs"}, {"symbol": "infy"}]}') == [
        "TCS",
        "INFY",
    ]
    assert parse_symbols('{"symbols": ["tcs", "infy"]}') == ["TCS", "INFY"]
    assert parse_symbols("{not json") == ["{NOT", "JSON"]
