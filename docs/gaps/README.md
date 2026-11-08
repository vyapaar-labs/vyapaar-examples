# Gap docs — `vyapaar-examples`

Per-repo gap ledger for stubs/mirrors/workarounds (workspace rule §9). Every gap
names the owning repo so that when the owning surface ships, closing the gap here
means deleting the mirrored code and re-pointing consumers.

Numbering is per-repo, sequential, never reused. Open an issue file
`NNNN-short-slug.md` here whenever a stage stubs/mirrors/hardcodes something.

## Ledger (plan `docs/plans/0002-honba-examples-staged-port.md` §4)

| # | Slug | Symptom | Owning repo | Status |
| :--- | :--- | :--- | :--- | :--- |
| 0001 | `0001-vyapaar-wheel-algo-analytics-surface` | `honba.algo_analytics.{walk_forward,folds,monte_carlo,deflated_sharpe}` have no `vyapaar` wheel equivalent → mirrored in `vyapaar_examples/optimizer/` + `quant.py` | `vyapaar-runtime` (enhancer crates) / `vyapaar-ffi` (wheel surface) | open (filed, Stage 1) |
| 0002 | `0002-vyapaar-wheel-ai-provider-surface` | `honba.ai.{ask,decision,llm.provider,autoresearch}` have no wheel equivalent → scripted/mirror paths; `02_autoresearch_loop` design-only | `vyapaar-agent` (research loop, llm adapters) / `vyapaar-ffi` | open (filed, Stage 1) |
| 0003 | `0003-vyapaar-data-nav-loaders` | `vyapaar_data` loaders/store/mutual-funds/coverage surface missing → in-repo `amfi.py` + `VYAAPAAR_DATA_DIR` test seam | `vyapaar-data` | open (filed, Stage 1) |
| 0004 | `0004-vyapaar-wheel-display-universes-client` | `honba.display`, `honba.markets.india.universes`, `honba.client`, `honba.cli.data` missing → mirrors in `display_style.py` / `universe_lists.py` / `cli.py` / `options/*` | `vyapaar-ffi` | open (filed, Stage 1) |
| 0005 | `0005-vyapaar-exec-freeze-slicer-mirror` | freeze-limit auto-slicing only mirrored; wheel `Sizer` cannot slice | `vyapaar-exec` (freeze slicer crate) / `vyapaar-ffi` | open (filed, Stage 6) |
| 0006 | `0006-vyapaar-wheel-kernel-domain-surface` | kernel-domain engine surface (types, Strategy contract, manifests/wire, store, evaluator, native attributes, indicator registry, declarative/execution/sizing, portfolio_strategy) absent from the wheel → `_kernel/` mirror + `native.py` pins | `vyapaar-ffi` | open (filed, Stage 1; extended Stage 2) |
| 0007 | `0007-vyapaar-adapters-framework-surface` | `honba.adapters` framework (contract/registry/capabilities/models/FakeAdapter/session/rate_limit/secrets) absent from the wheel → `_kernel/adapters/` mirror (13 files; `rest.py`+`gateway.py` excluded pending `honba.client` mirror) | `vyapaar-adapters` (connector packages) / `vyapaar-ffi` (wheel namespace) | open (filed, Stage 2) |
| 0008 | `0008-runtime-session-surface` | No wheel session orchestrator for real-data runs (next-open fills, NSE costs, T+1 settlement) → `_kernel/session.py` protocol-only stub; `Vyapaar.backtest` raises `NotImplementedError` on purpose | `vyapaar-runtime` (Strategy Tester session) / `vyapaar-ffi` (wheel surface) | open (filed, Stage 3) |

Status values: `reserved` (numbering held, not yet filed) · `open` (mirror/stub
is live in this repo; filing doc exists or lands with the referencing stage) ·
`closed` (owner shipped; delete the file with the mirror's removal — see the
closing commit).

Per gap doc template: status · what is stubbed/mirrored · why · how to close it.
