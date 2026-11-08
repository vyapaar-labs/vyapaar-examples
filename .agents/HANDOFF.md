# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Honba staged port (`docs/plans/0002-honba-examples-staged-port.md`)** — **ALL 9 STAGES COMPLETE (Stages 0–8)**:
  * **Stage 0 (pre-flight)** — deps and extras verified, gap tracking reserved.
  * **Stage 1 (shared harness)** — harness modules, kernel mirror `_kernel/`, unit tests; gaps 0001–0004 + 0006.
  * **Stage 2 (SDK fundamentals)** — `basic` 5, `candles` 4, `strategies` 16 scripts + tests.
  * **Stage 3 (tester & enhancer)** — `backtesting` 11, `optimizer` 3 scripts + tests, tester & enhancer mirrors.
  * **Stage 4 (lakehouse)** — `storage` 4, `universes` 10, `mutual_funds` 4 scripts + tests.
  * **Stage 5 (screeners)** — `screening` 8 scripts + chain recipes + research doc.
  * **Stage 6 (derivatives & StockSharp)** — `options` 8, `stocksharp` 5 scripts + tests.
  * **Stage 7 (AI research & production)** — `ai_research` 11, `production` 6 scripts + tests.
  * **Stage 8 (docs, index, suite sweep)** —
    * 13 topic READMEs complete (including `examples/options/README.md`); master index created at `examples/README.md`.
    * Concept docs ported to `docs/reference/` (`options_microstructure.md`, `roadmap-chaining.md`, `refactor-plan.md`).
    * Full test suite parity reached: 137 test modules (103 unit, 5 integration, 2 snapshot goldens).
    * `test_pitfalls_sections.py` enforces docstrings across all 94 topic scripts and 15 flat scripts.
    * Decoupling tests (`test_polyrepo_decoupling.py`) pass.
    * Sweep gate clean: zero imports or active identifiers of `honba` across `examples/`, `vyapaar_examples/`, `tests/`.
    * `docs/roadmap/roadmap.md` milestones closed; `docs/migration-guide.md` updated; `docs/plans/0002-honba-examples-staged-port.md` marked Implemented.
    * All verification gates green: `pytest -q` (922 passed, 70 skipped, 0 failures), `ruff check .` clean, `ruff format --check .` clean, `mypy vyapaar_examples` (234 files) clean, `make check` green.

## Decisions & Discoveries
* **Pytest import mode & test structure**: Adding `pythonpath = ["."]` in `pyproject.toml` and empty `__init__.py` in `tests/`, `tests/unit/`, and `tests/integration/` allows running `pytest -q` directly from the repo root and resolves module name collisions between unit and integration test directories.
* **Sharpe ratio scale invariance precision**: In `test_metrics_property.py`, `sharpe_ratio` property test uses `pytest.approx(scaled, rel=1e-5, abs=1e-6)` to accommodate standard float64 machine epsilon noise when scaling large-magnitude values (~100,000).
* **Pitfalls contract**: Flat foundational scripts (15) have 2–3 bullets while topic scripts (94) have 3–6 bullets. `test_pitfalls_sections.py` accommodates both correctly.
* **Offline catalog seam**: Integration tests that require the multi-GB real Parquet catalog gracefully skip when run in offline environments without data, maintaining offline test determinism.

## Immediate Next Step
* All 9 stages of the `honba-examples` port are complete and fully verified.
* Commit Stage 8 to git and create PR / merge branch.

## Operating Invariants
* Zero floats in financial math (documented exceptions: BS internals example 13; grafted `metrics.py` stats; kernel-mirror float domain, gap 0006). Deterministic offline runs; tests live in `tests/` only.
* Canonical verification: `pytest -q && ruff check . && ruff format --check . && mypy vyapaar_examples && make check`.
