# Refactor plan for `vyapaar-examples`

> **Status:** Completed during staged port. Plumbing extracted into `vyapaar_examples/`, lesson logic intact, R1/TDD followed.

## 0. Principles & constraints

- **Test-preserving first.** Do not change test expectations unless a behavior change is intentional and necessary.
- **Extract, don't erase lessons.** Move harness code (CLI, windowing, hashes/run.json, settlement, printing) into shared helpers; keep strategy/rebalance/math, coverage gates, and narrative docstrings in the example files.
- **Additive before destructive.** Create new helpers with unit tests first, switch examples to use them, only then delete in-file duplicates.
- **Keep imports working.** Re-export symbols so tests continue to work without test edits.

## 1. Shared Helpers

- `vyapaar_examples/settlement.py`: `resolve_settlement_days` precedence handling.
- `vyapaar_examples/catalog.py`: `load_named` strategy catalog loader.
- `vyapaar_examples/artifact.py`: `bars_digest`, `resolve_window`, `write_json_report`.
- `vyapaar_examples/synthetic.py`: shared test fixtures and bar generators.
- `vyapaar_examples/backtest.py`: simulated fills, costs, latency, analytics.
