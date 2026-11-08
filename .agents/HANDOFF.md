# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)** — 5 of 9 stages done:
  * **Stage 0 (pre-flight)** — commit `0be8298`, `feat/port-stage-0-preflight`.
  * **Stage 1 (shared harness)** — `feat/port-stage-1-harness-staged-port`:
    harness modules, merge-homes, kernel mirror `_kernel/`, 34 test files. Milestone detail
    lives in the branch/commits; gaps `0001`–`0004` + `0006` filed.
  * **Stage 2 (SDK fundamentals)** — `feat/port-stage-2-sdk-fundamentals`: `basic` 5 + `candles` 4 + `strategies` 16 scripts, 22 test files,
    3 topic READMEs ported; `_kernel/` extended with `adapters/` (13 files, gap 0007),
    `indicators/` (87 files), `declarative.py`, `execution.py`, `sizing.py`,
    `portfolio_strategy/` (10 files) — 128 new mirror files, all 138 ported modules import
    cleanly. Gates: `pytest` 424 passed / 94 skipped, `ruff check` + `ruff format --check`
    (334 files), `mypy vyapaar_examples` (202 files) — all green; stage filter passed
    (102 tests). Gaps 0006 extended + 0007 filed in the same change.
  * **Stage 3 (tester & enhancer)**: `backtesting` 11/11 + `optimizer` 3/3 scripts, 14 test
    files, 2 topic READMEs ported; `_kernel/` extended with `backtest/` (simulated fills,
    costs, latency), `markets/`, `log.py`, `risk.py`, `runner.py`, `session.py` (protocol
    stub, gap 0008); `optimizer/algo_analytics/` (walk-forward, Monte Carlo, DSR/PBO,
    plateau) grafted into `vyapaar_examples/backtest.py`. `docs/reference/{dsr_pbo,
    wfo_efficiency}.md` ported. Gates: `pytest` 509 passed / 110 skipped, `ruff check` +
    `ruff format --check`, `mypy vyapaar_examples` (222 files) — all green; stage filter
    (45 passed / 2 skipped). Two tests needing the real lakehouse catalog
    (`test_08_sip_buy_and_hold.py`, `test_10_chained_screener_and_sip.py`, 16 cases) skip
    cleanly via a `pytest.skip`-on-`FileNotFoundError` guard citing gap 0003. Gap 0008 filed.
  * **Stage 4 (lakehouse consumers)**: `storage` 4/4 (`01_parquet_catalog`,
    `02_import_nse_bhavcopy` + new `bhavcopy.py` dialect-sniffing parser,
    `03_import_amfi_nav`, `04_export_tearsheet`), `mutual_funds` 4/4
    (`01_fetch_nav`…`04_portfolio_optimization`) and `universes` 10/10
    (`01_nifty50_constituents`…`09_alpha30_cross_sectional` + shared
    `alpha30_constituents.py`) ported with tests and topic READMEs across
    commits `5019a91` (storage, mutual_funds) and `f2576c8` (universes); the
    three previously-gated `test_universe_lists.py` cases are activated now
    that the scripts exist. Gap `0003` extended (adds `bhavcopy.py`). Gates:
    `pytest` 583 passed / 108 skipped, `ruff check` + `ruff format --check`,
    `mypy vyapaar_examples` (223 files) — all green; stage filter
    (`parquet or bhavcopy or amfi or nav or universe or alpha30`) 86 passed /
    3 skipped.
  * **Stage 5 (screeners) — in progress**: `screening` 8/8 scripts landed
    (`01_multibagger_screener`…`08_swing_ap_setup_screener`) + `chains/` (3 TOMLs:
    `fundamentals`, `quality_value`, `multibagger_fundamentals`) + `01`'s dedicated
    test. `06_run_chain.py`'s `honba.strategies.loader.CatalogError` import mirrors
    to `_kernel.loader` citing gap 0006. Also fixed two latent bugs surfaced by
    un-skipping `tests/unit/test_screening_cli.py` (ported Stage 1, dormant while
    `examples/screening/` didn't exist): (1) 3 tests called
    `resolve_catalog_dir()`/`run()` with no real NSE catalog on disk and failed
    outright instead of skipping; reworked them to request a `_real_catalog` fixture
    mirroring `test_10_chained_screener_and_sip.py`'s pattern, citing gap 0003.
    (2) a missed D5 rename — `pytest.importorskip("honba_data", ...)` never matched
    any real package name, so the mutual-fund execution test always skipped for the
    wrong reason; renamed to `vyapaar_data` (still skips today, correctly, since that
    wheel isn't installed here — gap 0003). Gates: `pytest` 596 passed / 99 skipped,
    `ruff check` + `ruff format --check`, `mypy vyapaar_examples` (223 files) — all
    green; stage filter (`screener or chain or screening`) 64 passed / 38 skipped.
    Remaining: topic README + `docs/multibagger_screening_research.md`.
  * **Landed on `main`**: Stages 0–2 fast-forwarded `552c873 → 511da5a` (linear, no merge
    commit; `origin/main` unpushed at the time of merge). The three `feat/port-stage-*`
    branches remain as markers and can be deleted (`git branch -d`).
  * Remaining: finish Stage 5 (screeners) → Stage 8.

## Decisions & Discoveries
* **Two bar worlds coexist by design**: fresh pedagogy world is exact `Decimal`
  (`data.py`; examples import `synthetic_bars` from the package root) while the ported
  harness world is kernel-verbatim (`_kernel.bar.Bar` floats; `synthetic.py` verbatim to
  match `ewr`/`amfi`/`bars`). A "Decimal rewrite" of `synthetic.py` was tried and reverted
  in Stage 1 — it breaks the harness Bar contract at runtime.
* **Kernel mirror policy**: verbatim kernel modules under `_kernel/` with per-file
  `# ruff: noqa` headers, inline `# mirror accommodation (gap 0006)` `type: ignore[...]`
  comments, and a `# mirror: kernel-verbatim port (gap NNNN)` citation line after the
  docstring of every new mirror file. `native.py` pins `SCHEMA_VERSION = 8`,
  `API_VERSION = "v1"`, `STRATEGY_API_VERSION = "1.0.0"` (wheel absent — gap 0006).
* **`_kernel/entities.py` binds BOTH domain and wire re-exports** (wire last, mirroring
  tamashii `entities/__init__`): code that needs the FSM `OrderEvent` must import
  `_kernel.order_state` directly — importing it from `entities` silently resolves to the
  wire event and breaks `OrderEvent.submitted()/fill()/...` at type-check time.
* **`strategies/portfolio` → `_kernel/portfolio_strategy/`** rename (Stage 2): avoids the
  collision with the already-mirrored `_kernel/portfolio.py` domain module; all
  `honba.strategies.portfolio` imports retarget there. Likewise
  `honba.strategies import X` → `_kernel.declarative import X`; `sizing.py`/
  `execution.py` sit directly in `_kernel/`.
* **mypy override block** (Stage 2): `[[tool.mypy.overrides]]` in `pyproject.toml`
  disables `override` for `_kernel.indicators.*`, `_kernel.declarative`,
  `_kernel.portfolio_strategy.*` — the indicator registry decorates subclasses with
  typed `update(...)` signatures that intentionally specialize the base protocol
  (77 errors by design, not drift).
* **Port transformer gotchas** (`/tmp/opencode/port_stage2.py`): never append a trailing
  comment to a multi-line `from X import (` opener line — it corrupts syntax (gap
  citations only go on single-line imports); lint-fix closures that capture loop vars
  must bind via default parameters (ruff B023) *and* stay inferable to mypy (annotated
  `def` with default-arg binding, not a lambda with defaults — the lambda fails
  "cannot infer type of lambda").
* **Offline data seam** (gap 0003): `screening/paths.py` prepends `VYAAPAAR_DATA_DIR`,
  `tests/unit/conftest.py` supplies `catalog_dir`/`add_series`/`fund_db`/`data_env`
  fixtures; golden `output_report.txt` needs `VYAAPAAR_BLESS=1` to re-bless.
* **Deferred-topic tests skip** until their scripts land: `test_screening_cli` (Stage 5),
  `test_nl_support` + `decision_guard` 09 (ai_research topic). `02_autoresearch_loop`
  stays design-only pending `vyapaar-agent` (gap 0002). Stage-2 topics have no skips
  (fake-adapter offline).
* Digit-named example modules load via `importlib.util.spec_from_file_location`.
* Zero floats start at the source: fresh synthetic walks step in integer paise and
  materialize `Decimal`; ruff RUF032 forbids `Decimal(<float literal>)`; RUF002 keeps
  ambiguous unicode out of new docstrings (ASCII math).
* mypy `exclude` substring-matching: CI type-checks only `vyapaar_examples`.
* Black-Scholes (example 13) mirrors the pricing crate's documented exception:
  `math` floats internally, `Decimal` rounded to 8dp at the boundary.
* Local environment: **the `vyapaar` wheel is absent**; PEP-668 system python;
  optuna is the only missing optional dep — D7 `pytest.importorskip` keeps CI green.
  Examples run standalone (`PYTHONPATH=.`) or via rootdir conftest.
* **Real-catalog skip seam** (Stage 3, gap 0003): tests that need genuine lakehouse
  behaviour (e.g. `test_10_chained_screener_and_sip.py`'s point-in-time fundamentals
  sparsity checks) rather than synthetic `add_series` fixtures request a `_real_catalog`
  fixture that calls `find_catalog_path()`/reads the real `ParquetBarStore` and
  `pytest.skip`s with the gap citation on `FileNotFoundError`/empty read — mirrors the
  established `test_pipeline_chain.py` probe-and-skip pattern, not a new idiom.
* **`backtest.py` has two `Bar` names in scope** (Stage 3 bug, fixed): the grafted
  engine family (`run_portfolio_backtest`) takes kernel `_kernel.bar.Bar`
  (`Sequence[Bar]`), while the original `Backtest` class's `signal_fn`/`Trade` contract
  needs the fresh Decimal `data.Bar` (imported as `FreshBar`) — a stray `list[Bar]` on
  `Backtest.__init__` silently typo'd into the kernel type; watch for this when grafting
  more engine functions into this file.
* **`native_attr`-only dynamic modules need `# noqa: F822` on `__all__`, not a
  TYPE_CHECKING import**: `risk.py`/`manifest.py`/`money.py` expose Rust-native names
  (`RiskLimits`, `TradingState`, ...) only via module `__getattr__`; listing them in
  `__all__` needs `# noqa: F822 - lazy, see __getattr__` per name, and a TYPE_CHECKING
  self-import of the same module is always wrong (ruff/mypy both reject it).
* **`_kernel/session.py`'s `Vyapaar` class (gap 0008, Stage 3)** is a custom
  (non-verbatim) protocol-only stub for the absent `vyapaar-runtime` session
  orchestrator: `DataProvider`/`CostModel`/`BacktestResult` Protocols type the
  `algo_analytics` engines' real-data path, and `Vyapaar.backtest(...)` raises
  `NotImplementedError` on purpose (D7) — it was mis-ported once as `class Honba`
  (D4 rename missed), breaking the three consumers that already said `Vyapaar`.

## Immediate Next Step
* **Stage 4 (lakehouse consumers) is complete**: `storage` 4/4, `mutual_funds` 4/4 and
  `universes` 10/10 scripts ported with tests and topic READMEs. Next: Stage 5
  (screeners, `screening` 8 scripts) per `docs/plans/0002-honba-examples-staged-port.md`.

## Operating Invariants
* Zero floats in financial math (documented exceptions: BS internals example 13; grafted
  `metrics.py` stats; kernel-mirror float domain, gap 0006). Deterministic offline runs;
  tests live in `tests/` only.
* Ported topic scripts keep source file names verbatim; topic-relative slots never
  reused (`ai_research/08` reserved); flat `01`–`15` journey untouched.
* Fresh modules (`data.py`, `sdk.py`, `walkforward.py`, `_compat.py`) and the package
  export block are canonical — never re-copy them from the source repo.
* Ported-file custom edits listed in this file's history (merge-homes + grafts) must not
  be regenerated from the source; only splitter-touched verbatim modules may be
  re-regenerated via `/tmp/opencode` scripts.
* Never stage `examples/09_alpha30_factor_model.py` or
  `tests/unit/test_09_alpha30_factor_model.py` (concurrent session owns them).
