# `vyapaar-examples` — TDD & Engineering Roadmap

## Milestone 1: Remaining `honba-examples` Port (P0)
- [x] Fix `pyproject.toml` (remove invalid `rust_decimal` dependency).
- [x] Entry journey implemented fresh (flat `examples/01`–`15`, 8-module harness
      + per-example regression tests) — `docs/plans/0001` Layer 6.
- [ ] Execute the staged port `docs/plans/0002-honba-examples-staged-port.md`
      (Stages 0–8: pre-flight → shared harness → basic/candles/strategies →
      backtesting/optimizer → storage/universes/mutual-funds → screening →
      options/stocksharp → ai_research/production → docs & sweep). The old flat
      "copy all of `src/honba_examples` + `examples` + `tests`" instruction is
      superseded: the fresh `backtest.py`/`metrics.py` stay canonical, ported
      source capabilities get grafted in per the plan's overlap policy (D3).

## Milestone 2: Full Verification Suite (P0, closes with port Stage 8)
- [ ] Ported per-example unit tests (103 source modules), `tests/integration/`
      (5), `tests/snapshots/` goldens, and the `Pitfalls::` docstring-contract
      test scoped over topic dirs + flat scripts; `pytest -q`, `ruff check .`,
      `ruff format --check .`, `mypy vyapaar_examples` all green without the
      optional extras installed.
