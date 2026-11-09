# `vyapaar-examples` — Migration & DDD Refactoring Guide

> **Tier**: Tier 6D
> **Source**: `/home/pmallapp/Devel/Finance/honba-workspace/honba-examples`
> **Target**: `/home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples`
> **Status**: Migration complete (staged port, all 9 stages 0–8).

## Migration Status

The staged port (`docs/plans/0002-honba-examples-staged-port.md`, Stages 0–8) is **complete**:

- The fresh entry journey (`examples/01`–`15`, 8-module harness) is preserved as the introductory foundational path.
- All 13 topic directories (`examples/basic`, `candles`, `storage`, `universes`, `strategies`, `backtesting`, `optimizer`, `screening`, `mutual_funds`, `options`, `stocksharp`, `ai_research`, `production`) and their 94 scripts + topic READMEs are ported.
- Master index created at `examples/README.md`.
- Shared harness modules (`vyapaar_examples/`) grafted with source backtest, metrics, pipeline, screening, ewr, options, optimizer, and ai_replay capabilities.
- Full test suite ported (137 test modules across unit and integration suites + snapshots).
- Gaps 0001–0008 documented in `docs/gaps/`.

## Executed Verification Pipeline

```bash
cd /home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples
pytest -q
ruff check .
ruff format --check .
mypy vyapaar_examples
```

All verification gates pass cleanly without external network or broker dependencies:
- `pytest -q`: 922 passed, 70 skipped, 0 failures
- `ruff check .`: clean
- `ruff format --check .`: clean
- `mypy vyapaar_examples` (234 files): clean
- `make check`: green

## Migration Milestone Status

| Milestone | Status |
|-----------|--------|
| `pyproject.toml` fixed (invalid `rust_decimal` removed) | Complete |
| Entry journey (`examples/01`–`15`, 8-module harness) | Complete |
| Staged port Stage 0–8 (all 94 topic scripts) | Complete |
| Master index (`examples/README.md`) | Complete |
| Test suite (137 test modules) | Complete |
| Gaps 0001–0008 documented | Complete |
| `pytest -q` / `ruff` / `mypy` / `make check` | All green |
| Zero `honba` identifiers in `examples/`, `vyapaar_examples/`, `tests/` | Complete |
