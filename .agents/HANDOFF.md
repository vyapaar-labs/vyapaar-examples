# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)** — 3 of 9 stages done:
  * **Stage 0 (pre-flight)** — commit `0be8298`, `feat/port-stage-0-preflight`.
  * **Stage 1 (shared harness)** — `feat/port-stage-1-harness-staged-port` (stacked, unmerged):
    harness modules, merge-homes, kernel mirror `_kernel/`, 34 test files. Milestone detail
    lives in the branch/commits; gaps `0001`–`0004` + `0006` filed.
  * **Stage 2 (SDK fundamentals)** — `feat/port-stage-2-sdk-fundamentals` (stacked on
    Stage 1, unmerged): `basic` 5 + `candles` 4 + `strategies` 16 scripts, 22 test files,
    3 topic READMEs ported; `_kernel/` extended with `adapters/` (13 files, gap 0007),
    `indicators/` (87 files), `declarative.py`, `execution.py`, `sizing.py`,
    `portfolio_strategy/` (10 files) — 128 new mirror files, all 138 ported modules import
    cleanly. Gates: `pytest` 424 passed / 94 skipped, `ruff check` + `ruff format --check`
    (334 files), `mypy vyapaar_examples` (202 files) — all green; stage filter passed
    (102 tests). Gaps 0006 extended + 0007 filed in the same change.
  * Remaining: Stage 3 (tester & enhancer: `backtesting` 11, `optimizer` 3) → Stage 8.
    Stale earlier plan scratch (Tier 6D, Fincept/Quantcept Layer 6, port-plan availability)
    are completed milestones recorded in git history; their slice detail lives in the
    commits and `docs/plans/`.

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
  `test_nl_support` + `decision_guard` 09 (ai_research topic), `test_universe_lists`
  script tests (Stage 4). `02_autoresearch_loop` stays design-only pending
  `vyapaar-agent` (gap 0002). Stage-2 topics have no skips (fake-adapter offline).
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

## Immediate Next Step
* **Commit Stage 2** on `feat/port-stage-2-sdk-fundamentals`
  (`feat(examples): port stage 2 (SDK fundamentals: basic, candles, strategies)`,
  citing gaps 0004/0006/0007); verify `git add` excludes the concurrent session's
  `examples/09_alpha30_factor_model.py` + `tests/unit/test_09_alpha30_factor_model.py`.
* Then **Stage 3 (tester & enhancer)**: port `backtesting` 11 + `optimizer` 3 topics with
  their tests; `optimizer` scripts need the Stage-1 mirror `optimizer/`/`quant.py`
  (gap 0001) and `hypothesis` (already a dev dep). Stage 3 exercises
  `_kernel.testing.replay` reporting + walker/WSR/DSR mirror paths; check whether
  `honba.backtesting` scripts import anything beyond the existing `_kernel` groups
  before extending the mirror map.

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
