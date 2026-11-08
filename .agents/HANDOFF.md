# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)** — 3 of 9 stages landed:
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
  * **Remaining**: Stage 4 (lakehouse consumers), Stage 5 (screeners), Stage 6 (derivatives).

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
* **Graft boundary fix**: `run_portfolio_backtest`'s default `costs` parameter was shadowed
  by the fresh Decimal `nse_equity_delivery_fill_cost` defined in the same file; retargeted
  to the kernel Money-typed `_kernel_nse_equity_delivery_fill_cost` alias to pair correctly
  with the mirrored simulator.
* **Import alias handling**: `import honba.X as _honba_log` style aliases are renamed via a
  post-pass that detects `honba` in the alias name and replaces it with `vyapaar`/`_kernel`.

## Immediate Next Step
* **Stage 3 (tester & enhancer) is staged and ready to commit**. After commit: Stage 4
  (lakehouse consumers: `storage` 4, `mutual_funds` 4, `universes` 10) per
  `docs/plans/0002-honba-examples-staged-port.md`.

## Operating Invariants
* Zero floats in financial math (documented exceptions: BS internals example 13; grafted
  `metrics.py` stats; kernel-mirror float domain, gap 0006). Deterministic offline runs;
  tests live in `tests/` only.
* Never stage `examples/09_alpha30_factor_model.py` or `tests/unit/test_09_alpha30_factor_model.py`
  (concurrent session owns them).
* The `vyapaar` wheel is absent; examples run standalone (`PYTHONPATH=.`) or via rootdir conftest.
