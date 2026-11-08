# Examples Index

Runnable learning-path examples for Vyapaar. Every numbered script is
offline and deterministic by default — the `fake` adapter plus synthetic bars — and each one
teaches a single concept end to end.

Run every command below from the repo root:

```bash
pip install -e .
```

The examples cover both foundational scripts (the flat 01–15 learning path) and deep-dive
topics across 13 modular directories.

---

## Foundational Learning Path (`01`–`15`)

Canonical entry journey covering data loading, indicators, order lifecycle, bracket orders,
partial fills, factor models, options Greeks, and the AI research loop.

| # | File | Focus | What you learn |
|---|---|---|---|
| 01 | `01_loading_data.py` | Data Loading | Synthetic price series, coverage checks, Polars-backed CSV round-trip |
| 02 | `02_indicators.py` | Technical Indicators | Streaming SMA, EMA, and RSI calculation |
| 03 | `03_order_lifecycle.py` | Order Lifecycle | Submission, acknowledgement, partial fills, full fill, cancellation |
| 04 | `04_bracket_orders.py` | Bracket Orders | Entry limit order with coupled take-profit and stop-loss |
| 05 | `05_partial_fills.py` | Partial Fills | Multi-fill execution pacing across time intervals |
| 06 | `06_multi_symbol_portfolio.py` | Multi-Symbol Portfolio | Rebalancing across multiple instruments |
| 07 | `07_turtle_breakout_backtest.py` | Turtle Breakout | Donchian channels with 2N ATR trailing stop-loss |
| 08 | `08_nifty_options_microstructure.py` | Options Microstructure | ATM straddle backtest, Black-Scholes Greeks, contract note costs |
| 09 | `09_alpha30_factor_model.py` | Factor Model | Cross-sectional momentum-volatility factor scoring and top-decile portfolio |
| 10 | `10_walkforward_optimization.py` | Walk-Forward Optimization | Rolling train/test windows, Sharpe ratio, out-of-sample efficiency |
| 11 | `11_autoresearch_loop.py` | AI Research Loop | Hypothesis generation, backtest evaluation, and prompt cassettes |
| 12 | `12_portfolio_allocation.py` | Portfolio Allocation | Mean-variance optimization, Markowitz efficient frontier, risk parity |
| 13 | `13_black_scholes_greeks.py` | Black-Scholes Greeks | Exact analytical Greeks across spot price and volatility surfaces |
| 14 | `14_timeseries_forecast.py` | Time Series Forecasting | Autoregressive models and drift-adjusted trend projections |
| 15 | `15_fama_macbeth_factor_regression.py` | Factor Regression | Two-pass Fama-MacBeth cross-sectional factor risk premia estimation |

Run them:

```bash
python examples/01_loading_data.py
python examples/02_indicators.py
python examples/03_order_lifecycle.py
python examples/07_turtle_breakout_backtest.py
python examples/08_nifty_options_microstructure.py
python examples/10_walkforward_optimization.py
```

---

## `basic/` — Broker Adapters

Adapter mechanics only, no trading strategy.

| # | File | Shows |
|---|---|---|
| 01 | `01_connect_dhan.py` | Connect through the registry; print session and capabilities |
| 02 | `02_fetch_instruments.py` | Pull the instrument master (lot size, tick size) |
| 03 | `03_subscribe_quotes.py` | Stream live quotes and compare with snapshots |
| 04 | `04_place_order_paper.py` | Intent → report → fills, a cancel, a reject, the books |
| 05 | `05_check_positions.py` | Positions, funds and trades after a round trip |

Run them:

```bash
python examples/basic/01_connect_dhan.py
python examples/basic/02_fetch_instruments.py --query RELIANCE
python examples/basic/03_subscribe_quotes.py --advances 5
python examples/basic/04_place_order_paper.py --out orders.json
python examples/basic/05_check_positions.py
```

---

## `candles/` — Bar Construction

Bar ingestion, folding, and multi-timeframe aggregation.

| # | File | Shows |
|---|---|---|
| 01 | `01_historical_candles.py` | `historical_bars` over a half-open `[start, end)` |
| 02 | `02_realtime_candles.py` | Build OHLC frames from pushed quotes |
| 03 | `03_custom_aggregation.py` | The OHLC fold (`vyapaar_examples/bars.py`) |
| 04 | `04_multi_timeframe.py` | One fetch, many resolutions, alignment invariants |

Run them:

```bash
python examples/candles/01_historical_candles.py --timeframe 1m --instrument RELIANCE
python examples/candles/02_realtime_candles.py --advances 5
python examples/candles/03_custom_aggregation.py --timeframe 5m --out bars.json
python examples/candles/04_multi_timeframe.py
```

---

## `storage/` — Persistence

Lakehouse catalog, EOD Bhavcopy ingestion, and tearsheet exports.

| # | File | Strategy / purpose |
|---|---|---|
| 01 | `01_parquet_catalog.py` | `ParquetBarStore` layout and read/write contract |
| 02 | `02_import_nse_bhavcopy.py` | Parse exchange EOD Bhavcopy CSV into canonical bars |
| 03 | `03_import_amfi_nav.py` | Import AMFI `NAVAll.txt` into the store |
| 04 | `04_export_tearsheet.py` | Tearsheet generation: equity curve, drawdowns, and trade statistics |

Run them:

```bash
python examples/storage/01_parquet_catalog.py --data-dir /tmp/store
python examples/storage/02_import_nse_bhavcopy.py --data-dir /tmp/bhavcopy
python examples/storage/03_import_amfi_nav.py --data-dir /tmp/nav
python examples/storage/04_export_tearsheet.py --out-dir /tmp/tearsheet
```

---

## `universes/` — Universes and Equal-Weight Rebalancing

Index constituents, dynamic universe resolution, and periodic rebalancing.

| # | File | Strategy / purpose |
|---|---|---|
| 01 | `01_nifty50_constituents.py` | `resolve_universe("nifty50")` constituent resolution |
| 02 | `02_banknifty_constituents.py` | Thematic universe resolution for Bank Nifty |
| 03 | `03_alpha30_constituents.py` | `load_alpha30()` seed and helper |
| 04 | `04_alpha30_generic_rebalancer.py` | Generic universe equal-weight rebalancing |
| 05 | `05_alpha30_custom_universe.py` | Custom registered universe with equal-weight rebalancing |
| 06 | `06_alpha30_equal_weight_demo.py` | Alpha 30 specialization of generic rebalancer |
| 07 | `07_alpha30_backtest.py` | Backtest on `nifty200_alpha_30`, next-open fills, T+1 settlement |
| 08 | `08_alpha30_union_ewr_backtest.py` | Equal-weight rebalancer with close fills and statutory fee modeling |
| 09 | `09_alpha30_cross_sectional.py` | Momentum-volatility factor scores; monthly top-decile rebalance |

Run them:

```bash
python examples/universes/01_nifty50_constituents.py
python examples/universes/04_alpha30_generic_rebalancer.py
python examples/universes/06_alpha30_equal_weight_demo.py
python examples/universes/07_alpha30_backtest.py --test-start 2026-06-01 --out-dir /tmp/alpha30
python examples/universes/08_alpha30_union_ewr_backtest.py --start 2026-01-01 --end 2026-09-23
```

---

## `strategies/` — Reference Strategies

Declarative and procedural strategies run on synthetic replay.

| # | File | Strategy class | Indicators / parts |
|---|---|---|---|
| 01 | `01_first_strategy.py` | `SmaCrossover` | SMA (fast/slow) |
| 02 | `02_with_indicators.py` | `CompositeSmaRsi` | SMA/EMA + RSI filter + ATR sizing + trailing stop |
| 03 | `03_position_sizing.py` | `SmaSizing` | SMA + ATR; fixed / volatility / fractional-Kelly sizing |
| 04 | `04_risk_management.py` | `RiskManagedSma` | SMA + drawdown, daily-loss and position guards |
| 05 | `05_multi_instrument.py` | `BasketSma` | SMA per symbol + equal-weight rebalance |
| 06 | `06_equal_weight_rebalance.py` | `PortfolioStrategy` | `NamedUniverse` + `EqualWeight`/`InverseVolatility` + `EveryNDays` |
| 07 | `07_declarative_long_short.py` | `LongShortCrossover` | `DeclarativeStrategy`; long/short SMA crossover + stop and target |
| 12 | `12_buy_and_hold_lifecycle.py` | `BuyAndHold` | Canonical lifecycle hooks: `on_start`, `on_bar`, and `on_stop` |
| 13 | `13_bracket_order_mis.py` | `BracketOrderMis` | Bracket orders + MIS intraday margin with 15:20 IST auto-square-off |
| 14 | `14_partial_fill_handling.py` | `PartialFillStrategy` | Order lifecycle events (`on_order_event`), partial fill accounting |
| 15 | `15_multi_symbol_portfolio.py` | `MultiSymbolPortfolio` | Multi-symbol portfolio across 5 NIFTY scrips with per-symbol sizing |
| 16 | `16_dynamic_position_sizing.py` | `DynamicPositionSizing` | Fixed lot vs fixed fractional vs ATR volatility targeting |

Run them:

```bash
python examples/strategies/01_first_strategy.py
python examples/strategies/02_with_indicators.py --rsi-period 14 --use-ema
python examples/strategies/03_position_sizing.py --sizing volatility
python examples/strategies/04_risk_management.py --max-drawdown-pct 0.15
python examples/strategies/05_multi_instrument.py --rebalance-every 15
python examples/strategies/06_equal_weight_rebalance.py --rebalance-days 10
python examples/strategies/14_partial_fill_handling.py --target-qty 20
python examples/strategies/15_multi_symbol_portfolio.py --max-weight 0.20
python examples/strategies/16_dynamic_position_sizing.py --compare
```

---

## `backtesting/` — End-to-End Simulation

Event-driven backtesting with Indian statutory cost schedules and fill latency models.

| # | File | Strategy class | Adds |
|---|---|---|---|
| 01 | `01_first_backtest.py` | `SmaBacktest` | Next-open fills (`fill_delay=1`), capital sizing, gross/net P&L |
| 02 | `02_cost_modeling.py` | — | Per-leg statutory cost breakdown (brokerage, STT, exchange, SEBI, stamp, GST) |
| 03 | `03_latency_modeling.py` | `SmaLatency` | Fill models: bar_close / next_open / open_after_2_bars |
| 04 | `04_walk_forward.py` | `SmaWalk` | Rolling in-sample → out-of-sample windows, scored by net return |
| 05 | `05_monte_carlo.py` | `SmaMonteCarlo` | Bootstrap closed trades (final equity, drawdown distribution, Sharpe) |
| 06 | `06_concurrent_backtest.py` | `SmaSweep` | Parameter sweep across worker threads, Pareto frontier |
| 07 | `07_run_via_client.py` | — | Strategy execution across client transports |
| 08 | `08_sip_buy_and_hold.py` | — | Systematic investment plan (SIP): monthly/weekly buy-and-hold, XIRR |
| 09 | `09_forward_sip_backtest.py` | — | Forward SIP backtester (stdin pipe or `--symbols`) |
| 10 | `10_chained_screener_and_sip.py` | — | Chained screener (momentum, value, dividend) & forward SIP backtest |
| 11 | `11_portfolio_rebalancer.py` | — | Equal-weight periodic rebalance via `ewr` simulator (flat fee, T+1) |

Run them:

```bash
python examples/backtesting/01_first_backtest.py --out first_backtest.json
python examples/backtesting/02_cost_modeling.py --price 2500 --qty 10
python examples/backtesting/03_latency_modeling.py
python examples/backtesting/04_walk_forward.py --synthetic --train-months 12 --test-months 3 --n-folds 4
python examples/backtesting/05_monte_carlo.py --synthetic --offsets 0 5 10 20
python examples/backtesting/06_concurrent_backtest.py --workers 4
python examples/backtesting/08_sip_buy_and_hold.py --symbol ALPHAETF --frequency monthly --sip-amount 5000
python examples/backtesting/10_chained_screener_and_sip.py --strategy multibagger --asof 2023-01-01 --top 5
```

---

## `optimizer/` — Parameter Search & Overfitting Diagnostics

Genetic algorithms, Bayesian optimization, and probabilistic overfitting diagnostics.

| # | File | Shows |
|---|---|---|
| 01 | `01_ga_trend_breakout.py` | Genetic Algorithm optimization of Donchian breakout; Pareto frontier |
| 02 | `02_bayesian_mean_reversion.py` | Bayesian TPE optimization of RSI mean-reversion |
| 03 | `03_deflated_sharpe_analysis.py` | Deflated Sharpe Ratio (DSR) & Probability of Backtest Overfitting (PBO) |

Run them:

```bash
python examples/optimizer/01_ga_trend_breakout.py --generations 50 --population 50
python examples/optimizer/02_bayesian_mean_reversion.py --trials 100
python examples/optimizer/03_deflated_sharpe_analysis.py --trials 100 --folds 5
```

---

## `screening/` — Point-in-Time Screeners and Chains

Screeners read 1D Parquet catalog and `fundamentals.duckdb` point-in-time.

| # | File | Adds |
|---|---|---|
| 01 | `01_multibagger_screener.py` | Stage 2 momentum breakout candidates; QGLP fundamental overlay |
| 02 | `02_value_52w_low_screener.py` | Deep value near 52-week low |
| 03 | `03_dividend_yield_screener.py` | High dividend yielders near 52-week low |
| 04 | `04_intelligent_investor_screener.py` | Graham value and margin of safety |
| 05 | `05_net_net_screener.py` | Graham net-net (NCAV) deep asset value |
| 06 | `06_run_chain.py` | Multi-step screen, filter, size, execute chain from TOML |
| 08 | `08_swing_ap_setup_screener.py` | Swing-trading A+ setup: breakout/pullback, relative strength, volume |

Run them:

```bash
python examples/screening/03_dividend_yield_screener.py --asof 2025-03-01 --top 5 --format symbols
python examples/screening/06_run_chain.py --chain examples/screening/chains/quality_value.toml --validate-only
python examples/screening/06_run_chain.py --chain examples/screening/chains/quality_value.toml --format csv
python examples/screening/06_run_chain.py --describe
```

---

## `mutual_funds/` — NAV and Systematic Investment

AMFI NAV data ingestion, rolling category analysis, and portfolio optimization.

| # | File | Purpose |
|---|---|---|
| 01 | `01_fetch_nav.py` | AMFI NAV history; daily resampling and missing session handling |
| 02 | `02_sip_backtest.py` | Fixed-date monthly SIP, unit accumulation at NAV, XIRR |
| 03 | `03_category_analysis.py` | Category performance statistics, rolling returns, quartile ranking |
| 04 | `04_portfolio_optimization.py` | Mean-variance allocation with diversification constraints |

Run them:

```bash
python examples/mutual_funds/01_fetch_nav.py --scheme 120503 --start 2023-01-01 --end 2024-12-31
python examples/mutual_funds/02_sip_backtest.py --scheme 120503 --monthly 10000 --start 2023-01-01
python examples/mutual_funds/03_category_analysis.py --category "Equity:Large Cap" --start 2020-01-01
python examples/mutual_funds/04_portfolio_optimization.py --schemes 120503,120504,120505 --start 2022-01-01
```

---

## `options/` — Option Chain, Greeks, and Strategies

Option chain construction, Black-Scholes Greeks, straddles, iron condors, and freeze-limit slicing.

| # | File | Strategy |
|---|---|---|
| 01 | `01_option_chain.py` | Chain snapshot; filter by expiry, strike, and moneyness |
| 02 | `02_greeks_calculation.py` | Black-Scholes Greeks per contract |
| 03 | `03_backtest_straddle.py` | Long ATM straddle held to expiry |
| 04 | `04_backtest_iron_condor.py` | 4-leg credit spread iron condor |
| 05 | `05_expiry_day_strategy.py` | Intraday gamma scalping on expiry day |
| 06 | `06_nifty_920_straddle.py` | Short ATM straddle at 09:20 IST; 25% stop-loss, 15:20 square-off; STT |
| 07 | `07_large_qty_options_slicer.py` | Freeze-limit slicer: 5,000 contracts sliced <= freeze limit (1,800) |
| 08 | `08_iron_condor_hedging.py` | Delta-hedged iron condor with Greek risk bounds |

Run them:

```bash
python examples/options/01_option_chain.py
python examples/options/02_greeks_calculation.py --spot 24500 --strike 24500 --dte 7 --iv 0.15
python examples/options/03_backtest_straddle.py --strike 24500 --entry-dte 7
python examples/options/04_backtest_iron_condor.py --wings 200
python examples/options/05_expiry_day_strategy.py --dte 0 --step 10
python examples/options/06_nifty_920_straddle.py --spot 22000 --iv 0.15 --out straddle.json
python examples/options/07_large_qty_options_slicer.py --total-qty 5000 --out slices.json
python examples/options/08_iron_condor_hedging.py --spot 24000 --wings 200 --dte 7 --out hedge.json
```

---

## `stocksharp/` — Ported StockSharp Reference Strategies

Canonical algorithmic strategies ported from StockSharp to the Vyapaar SDK.

| # | File | Strategy |
|---|---|---|
| 01 | `01_pairs_trading.py` | Statistical pairs trading: Engle-Granger cointegration, z-score entry/exit |
| 02 | `02_twap_vwap.py` | Execution slicers: TWAP and VWAP intraday pacing with microsecond jitter |
| 03 | `03_turtle_breakout.py` | Turtle system: 20/55-day Donchian breakout, 2N ATR trailing stops |
| 04 | `04_market_maker.py` | Avellaneda-Stoikov reservation price and quoting with order book imbalance |
| 05 | `05_risk_parity.py` | Risk-parity rebalancing across 10 scrips via inverse-volatility weights |

Run them:

```bash
python examples/stocksharp/01_pairs_trading.py --symbol-a ICICIBANK --symbol-b HDFCBANK --bars 252
python examples/stocksharp/02_twap_vwap.py --scheme twap --parent-qty 5000 --slices 75
python examples/stocksharp/02_twap_vwap.py --scheme vwap --parent-qty 5000 --slices 75 --seed 7
python examples/stocksharp/03_turtle_breakout.py --entry-window 20 --exit-window 10 --bars 200
python examples/stocksharp/04_market_maker.py --steps 240 --seed 42 --gamma 0.1 --k 1.5
python examples/stocksharp/05_risk_parity.py --symbols 10 --bars 260 --rebalance-days 20 --seed 42
```

---

## `ai_research/` — AI-Native Autonomous Research Loop

Typed decision loop using `ScriptedFakeLlm` (no external API keys required).

| # | File | Shows |
|---|---|---|
| 01 | `01_llm_research_analyst.py` | Natural language question -> validated screener filter via `ScriptedFakeLlm` |
| 06 | `06_mcp_integration.py` | Static MCP tool schema enumeration |
| 09 | `09_typed_llm_decision.py` | Typed `LlmDecision` (veto/size-down) on order intent; audit journaling |
| 10 | `10_claude_autonomous_quant.py` | MCP quant agent: hypothesis generation, backtest, and DSR evaluation |
| 11 | `11_deterministic_ai_replay.py` | Cryptographic prompt replayer: SHA-256 prompt cache + NDJSON journal |
| 12 | `12_ai_drawdown_refinement.py` | AI auto-enhancer: drawdown diagnosis, ADX trend filter, DSR re-evaluation |

Run them:

```bash
python examples/ai_research/01_llm_research_analyst.py --query "rsi below 30" --fake-response "rsi < 30"
python examples/ai_research/06_mcp_integration.py
python examples/ai_research/10_claude_autonomous_quant.py --underlying RELIANCE --seed 42
python examples/ai_research/11_deterministic_ai_replay.py --decisions 10 --seed 42
python examples/ai_research/12_ai_drawdown_refinement.py --seed 42 --out refinement.json
```

---

## `production/` — Paper & Live Deployment

Paper execution, broker connectivity templates, multi-account routing, and telemetry.

| # | File | Shows |
|---|---|---|
| 01 | `01_paper_trading.py` | Paper runner with Dhan adapter |
| 02 | `02_live_trading_dhan.py` | Live order submission template with pre-trade risk checks |
| 03 | `03_multi_account_execution.py` | Mirroring order intents across master and child accounts |
| 04 | `04_monitoring.py` | Heartbeat health endpoint, Prometheus metrics, alerting |
| 05 | `05_deployment.py` | Production deployment configuration and service management |
| 06 | `06_multi_broker_dispatch.py` | Strategy dispatch across Zerodha, Angel One, and Upstox adapters |

Run them:

```bash
python examples/production/01_paper_trading.py --broker dhan
python examples/production/04_monitoring.py --port 9090
python examples/production/06_multi_broker_dispatch.py --brokers zerodha,angelone,upstox --bars 120
```
