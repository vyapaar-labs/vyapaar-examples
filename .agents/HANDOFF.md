# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)** — 4 of 9 stages landed:
  * **Stage 0 (pre-flight)** — commit `0be8298`, `feat/port-stage-0-preflight`.
  * **Stage 1 (shared harness)** — `feat/port-stage-1-harness-staged-port`: harness modules,
    merge-homes, kernel mirror `_kernel/`, 34 test files; gaps `0001`–`0004` + `0006` filed.
  * **Stage 2 (SDK fundamentals)** — `feat/port-stage-2-sdk-fundamentals`: `basic` 5 + `candles` 4
    + `strategies` 16 scripts, 22 test files, 3 topic READMEs; `_kernel/` extended with
    `adapters/` (13 files, gap 0007), `indicators/` (87 files), `declarative.py`,
    `execution.py`, `sizing.py`, `portfolio_strategy/` (10 files) — 128 new mirror files.
    Gates: `pytest` 424 passed / 94 skipped, `ruff` + `mypy` green.
  * **Stage 3 (tester & enhancer)** — `feat/port-stage-3-tester-enhancer`: `backtesting` 11/11 +
    `optimizer` 3/3 scripts, 14 test files, 2 topic READMEs; `_kernel/` extended with
    `backtest/` (simulated fills, costs, latency), `markets/`, `log.py`, `risk.py`,
    `runner.py`, `session.py` (protocol stub, gap 0008); `optimizer/algo_analytics/`
    (walk-forward, Monte Carlo, DSR/PBO, plateau) grafted into `vyapaar_examples/backtest.py`.
    `docs/reference/{dsr_pbo,wfo_efficiency}.md` ported. Gates: `pytest` 638 passed / 99
    skipped (1 pre-existing failure), `ruff` (5 docstring E501 acceptable), `mypy` green.
    Gap 0008 filed; gaps 0001/0004/0006 extended. Branch `feat/port-stage-3-tester-enhancer`
    created and staged below.
  * **Stage 6 (derivatives & StockSharp)** — `feat/port-stage-6-derivatives-stocksharp`:
    `options` 8 scripts already ported; `stocksharp` 5/5 scripts + 5 tests ported:
    04_market_maker (Avellaneda-Stoikov quoting, OBI filter), 05_risk_parity (inverse-vol
    risk parity via `PortfolioStrategy`), 01_pairs_trading, 02_twap_vwap, 03_turtle_breakout.
    Gates: `pytest` 649 passed / 99 skipped (1 pre-existing), `ruff` + `ruff format`,
    `mypy` (229 files). No new gaps; gaps 0001/0004/0006/0008 cited.
  * **Stage 7 (AI research & production)** — `feat/port-stage-7-ai-production`:
    `ai_research` 11 scripts (01-03, 06, 09-12 runnable offline; 02, 04, 05, 07 design-only
    with pytest.skip + gap 0002) and `production` 6 scripts (01 paper trading, 02 Dhan template,
    03 multi-account, 04 monitoring, 05 deployment, 06 multi-broker dispatch).
    Added kernel mirrors for `_kernel/ai/` (ask, knowledge, decision, llm.provider),
    `_kernel/cli/` (ParquetBarStore integration), `_kernel/data/` (Quantity parser),
    and `_kernel/screener/` (catalog, coverage).
    Gates: `pytest` 62 passed in Stage 7 suite + 49 in nl_support, `ruff` + `ruff format` clean,
    `mypy vyapaar_examples` (234 files) clean.
  * **Remaining**: Stage 8 (Docs, index, sweep).

## Decisions & Discoveries
* **Two bar worlds coexist by design**: fresh pedagogy world is exact `Decimal`
  (`data.py`; examples import `synthetic_bars` from the package root) while the ported
  harness world is kernel-verbatim (`_kernel.bar.Bar` floats; `synthetic.py` verbatim to
  match `ewr`/`amfi`/`bars`). A "Decimal rewrite" of `synthetic.py` was tried and reverted
  in Stage 1 — it breaks the harness Bar contract at runtime.
* **Kernel mirror policy**: verbatim kernel modules under `_kernel/` with per-file
  `# ruff: noqa` headers, inline `# mirror accommodation (gap NNNN)` `type: ignore[...]`
  comments, and a `# mirror: kernel-verbatim port (gap NNNN)` citation line after the
  docstring of every new mirror file. `native.py` pins `SCHEMA_VERSION = 8`,
  `API_VERSION = "v1"`, `STRATEGY_API_VERSION = "1.0.0"` (wheel absent — gap 0006).
* **Native surface probe pattern** (gap 0006): `native_attr()` raises `RuntimeError` (not
  `AttributeError`) so callers can `try/except RuntimeError` and fall back to pure-Python
  when the kernel extension is missing/stale.
* **`_kernel/session.py`'s `Vyapaar` class (gap 0008)** is a custom protocol-only stub for
  the absent `vyapaar-runtime` session orchestrator: `DataProvider`/`CostModel`/`BacktestResult`
  Protocols type the `algo_analytics` engines' real-data path, and `Vyapaar.backtest(...)`
  raises `NotImplementedError` on purpose (D7).
* **Graft boundary fix** (Stage 3): `run_portfolio_backtest`'s default `costs` parameter
  was shadowed by the fresh Decimal `nse_equity_delivery_fill_cost` defined in the same
  file; retargeted to the kernel Money-typed `_kernel_nse_equity_delivery_fill_cost` alias
  to pair correctly with the mirrored simulator.
* **Import alias handling** (Stage 3): `import honba.X as _honba_log` style aliases are
  renamed via a post-pass that detects `honba` in the alias name and replaces it with
  `vyapaar`/`_kernel`.
* **PortfolioStrategy import fix** (Stage 6): `stocksharp/05_risk_parity.py` incorrectly
  imported `PortfolioStrategy` from `_kernel.declarative`; corrected to `_kernel.portfolio_strategy`.
  `PortfolioStrategy` is not exposed from `declarative.py` — it lives in `portfolio_strategy/`.
* **Stage 7 Kernel Mirrors & Config Patterns**:
  * Mirrored `_kernel/ai/` (`ask.py`, `knowledge.py`, `decision.py`, `llm/provider.py`),
    `_kernel/cli/` (`_STORE = ParquetBarStore()`), `_kernel/data/` (`parse_quantity`), and
    `_kernel/screener/` (`catalog.py`, `coverage.py`).
  * Used plain classes instead of dataclasses for `ZerodhaConfig` and `AngelOneConfig`
    in `06_multi_broker_dispatch.py` to prevent Python 3.14 dynamic module execution
    attribute lookup issues.
  * Kept `02_autoresearch_loop.py`, `04_nl_to_strategy.py`, `05_rl_training.py`, and
    `07_natural_language_critique.py` as design-only with `pytest.skip` + gap 0002 citation.

## Immediate Next Step
* **Stage 7 (AI research & production) is complete and committed on `feat/port-stage-7-ai-production`**.
  Next: Stage 8 (Docs, index, suite sweep) per `docs/plans/0002-honba-examples-staged-port.md`.

## Operating Invariants
* Zero floats in financial math (documented exceptions: BS internals example 13; grafted
  `metrics.py` stats; kernel-mirror float domain, gap 0006). Deterministic offline runs;
  tests live in `tests/` only.
* Never stage `examples/09_alpha30_factor_model.py` or `tests/unit/test_09_alpha30_factor_model.py`
  (concurrent session owns them).
* The `vyapaar` wheel is absent; examples run standalone (`PYTHONPATH=.`) or via rootdir conftest.
