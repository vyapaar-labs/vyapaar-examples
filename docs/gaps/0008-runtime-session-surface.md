# 0008 — runtime-session-surface

**Status**: open
**Owning repo**: `vyapaar-runtime` (Strategy Tester session orchestrator) /
`vyapaar-ffi` (wheel surface).

## Symptom
The `vyapaar` wheel does not ship a session orchestrator that can run a strategy
against real (lakehouse) data with next-open fills, NSE delivery costs and T+1
settlement from outside `vyapaar-runtime` itself. The Stage 3 optimizer engine
mirrors (`vyapaar_examples/optimizer/algo_analytics/{walk_forward,monte_carlo,
plateau}.py`) need exactly that surface for their real-data code path: each calls
`Vyapaar.backtest(...)` for a fold/trial/grid-point run.

## What stands in (mirror)
`vyapaar_examples/_kernel/session.py` — a custom (non-verbatim) trim pinning only
the static protocol shape the engine mirrors read against:
* `DataProvider` (Protocol): `bars(instrument_id, *, timeframe, start, end)`,
  `instrument(instrument_id)`.
* `CostModel` (Protocol): `apply(trade) -> Trade`.
* `BacktestResult` (Protocol): `strategy_name`, `metrics`, `equity_curve`.
* `Vyapaar`: a session-factory stub. `Vyapaar.backtest(...)` raises
  `NotImplementedError` unconditionally — loud failure by design (D7), matching
  the wheel-missing state, rather than a silent synthetic fallback.

This keeps the walk-forward/Monte-Carlo/plateau engines fully type-checkable and
runnable end-to-end on synthetic data (via `_kernel.testing.replay`, not
`Vyapaar.backtest`); only the real-data orchestration path is blocked, and it
fails with a clear message naming this gap.

## Consumers
`vyapaar_examples/optimizer/algo_analytics/walk_forward.py` (`_run_factory`'s
`run` closure), `monte_carlo.py`, `plateau.py` — each lazily imports
`_kernel.session.Vyapaar` only inside the real-data branch, so synthetic-data
callers never touch this stub.

## How to close
Ship the Strategy Tester session surface through `vyapaar-ffi` (a `vyapaar`
wheel class equivalent to `Vyapaar.backtest(strategy, start, end, ...)` that
runs next-open fills with NSE delivery costs and T+1 settlement against the
lakehouse). Then delete `_kernel/session.py`, retarget the three
`algo_analytics` consumers' `from vyapaar_examples._kernel.session import
Vyapaar` to the wheel surface, and drop the `NotImplementedError` branch.
