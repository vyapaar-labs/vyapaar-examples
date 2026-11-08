# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)**:
  * **Stage 0 (pre-flight) DONE** — commit `0be8298` on
    `feat/port-stage-0-preflight`: pyproject adds `vyapaar-adapters` dep +
    optional extras `ai`/`optimizer` (optuna+scipy+matplotlib), `mutual-funds`
    (scipy), `screening` (duckdb), dev `hypothesis`.
  * **Stage 1 (shared harness) DONE** on `feat/port-stage-1-harness-staged-port`
    (not yet committed-to-main): ~44 harness modules ported verbatim (D4/D5),
    merge-homes (`decision_guard`, `display_style`, `universe_lists`,
    `settlement`) + grafts (`metrics.py` source-stats, `backtest.py`
    canonical_hash + `nse_equity_delivery_fill_cost`, `fake_llm`, fresh
    `__init__` export block restored), kernel mirror `_kernel/` (now incl.
    `loader.py`/`config.py`), `HonbaExample` → `VyapaarExample`, 34 test files +
    `tests/unit/conftest.py` + `tests/snapshots/output_report.txt` ported.
    Gates: `pytest` 248 passed / 94 skipped (stage gate 119 passed/41 skipped),
    `ruff check`, `ruff format --check` (166 files), `mypy vyapaar_examples`
    89 files — all green. Gaps `0001`–`0004` + `0006` filed in `docs/gaps/`
    (`0005` reserved for Stage 5).
  * Remaining stages 2–8 not started. Stale earlier plan scratch (Tier 6D,
    Fincept/Quantcept Layer 6, port-plan availability) are completed
    milestones recorded in git history; their slice detail lives in the
    commits and `docs/plans/`.

## Decisions & Discoveries
* **Two bar worlds coexist by design**: the fresh pedagogy world is exact
  `Decimal` (`data.py` `Bar(instrument=str, …)`; examples import
  `synthetic_bars` from the package root) while the ported harness world is
  kernel-verbatim (`_kernel.bar.Bar(instrument_id=…)` floats; `synthetic.py`
  regenerated verbatim to match `ewr`/`amfi`/`bars` consumers). The earlier
  "Decimal rewrite" of `synthetic.py` was reverted — it broke the harness Bar
  contract (`bar.instrument_id`) at runtime.
* **Kernel mirror policy**: verbatim kernel modules under `_kernel/` with
  per-file `# ruff: noqa` headers and inline `# mirror accommodation (gap 0006)`
  `type: ignore[...]` comments; `_kernel/native.py` pins `SCHEMA_VERSION = 8`,
  `API_VERSION = "v1"`, `STRATEGY_API_VERSION = "1.0.0"` (wheel absent — see
  gap 0006). `catalog.py` lazy-imports `_kernel.loader`.
* **Offline data seam** (gap 0003): `screening/paths.py` prepends
  `VYAAPAAR_DATA_DIR` (`DATA_DIR_ENV`) to the catalog / `fundamentals.duckdb`
  / `mutual_funds.duckdb` discovery lists; `tests/unit/conftest.py` supplies
  `catalog_dir`/`add_series`/`fund_db`/`data_env` fixtures (dataset tests
  inject `catalog_dir=` per step; the source's `honba-data` real-data checkout
  does not exist here). Snapshot golden `output_report.txt` needs
  `VYAAPAAR_BLESS=1` to re-bless.
* **Deferred-topic tests skip** (`pytest.skip`/module-level `skipif`) until
  their scripts land: `test_screening_cli` (Stage 5 scripts),
  `test_nl_support` + `decision_guard` 09 (ai_research topic),
  `test_universe_lists` script tests (Stage 4). `02_autoresearch_loop` stays
  design-only pending `vyapaar-agent` (gap 0002).
* Digit-named example modules load via `importlib.util.spec_from_file_location`.
* Zero floats start at the source: fresh synthetic walks step in integer paise
  and materialize `Decimal`; ruff RUF032 forbids `Decimal(<float literal>)`.
* RUF002 is live: new docstrings keep ambiguous unicode out (ASCII math).
* mypy `exclude` substring-matching: CI type-checks only `vyapaar_examples`.
* Black-Scholes (example 13) mirrors the pricing crate's documented exception:
  `math` floats internally, `Decimal` rounded to 8dp at the boundary.
* Local environment: **the `vyapaar` wheel is absent**; PEP-668 system python;
  optuna is the only missing optional dep — D7 `pytest.importorskip` keeps CI
  green. Examples run standalone (`PYTHONPATH=.`) or via rootdir conftest.

## Immediate Next Step
* **Commit Stage 1** on `feat/port-stage-1-harness-staged-port` with a semantic
  message citing gaps 0001–0004/0006; verify `git add` excludes the concurrent
  session's `examples/09_alpha30_factor_model.py` +
  `tests/unit/test_09_alpha30_factor_model.py`.
* Then **Stage 2 (SDK fundamentals)**: `basic` 5, `candles` 4, `strategies` 16
  scripts onto the wheel surface + `vyapaar_adapters.registry`; port the ~25
  `test_NN_*.py` slot-for-slot; stage gate
  `-k "connect_dhan or fetch_instruments or subscribe_quotes or place_order or
  check_positions or first_strategy or with_indicators or position_sizing or
  risk_management or multi_instrument or bracket_order or partial_fill or
  lifecycle"`.

## Operating Invariants
* Zero floats in financial math (documented exceptions: BS internals example
  13; grafted `metrics.py` stats; kernel-mirror float domain, gap 0006).
  Deterministic offline runs; tests live in `tests/` only.
* Ported topic scripts keep source file names verbatim; topic-relative slots
  never reused (`ai_research/08` reserved); flat `01`–`15` journey untouched.
* Fresh modules (`data.py`, `sdk.py`, `walkforward.py`, `_compat.py`) and the
  package export block are canonical — never re-copy them from the source repo.
* Ported-file custom edits listed in `.agents/HANDOFF.md` history (merge-homes
  + grafts) must not be regenerated from the source; only splitter-touched
  verbatim modules may be re-regenerated via `/tmp/opencode` scripts.
* Never stage `examples/09_alpha30_factor_model.py` or
  `tests/unit/test_09_alpha30_factor_model.py` (concurrent session owns them).
