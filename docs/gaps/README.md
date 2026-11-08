# Gap docs — `vyapaar-examples`

Per-repo gap ledger for stubs/mirrors/workarounds (workspace rule §9). Every gap
names the owning repo so that when the owning surface ships, closing the gap here
means deleting the mirrored code and re-pointing consumers.

Numbering is per-repo, sequential, never reused. Open an issue file
`NNNN-short-slug.md` here whenever a stage stubs/mirrors/hardcodes something.

## Reserved numbering (plan `docs/plans/0002-honba-examples-staged-port.md` §4)

| # | Slug | Symptom (planned) | Owning repo | Status |
| :--- | :--- | :--- | :--- | :--- |
| 0001 | `0001-vyapaar-wheel-algo-analytics-surface` | `honba.algo_analytics.{walk_forward,folds,monte_carlo,deflated_sharpe}` have no `vyapaar` wheel equivalent → mirrored in `vyapaar_examples/optimizer/` + `quant.py` | `vyapaar-runtime` (enhancer crates) / `vyapaar-ffi` (wheel surface) | open |
| 0002 | `0002-vyapaar-wheel-ai-provider-surface` | `honba.ai.{ask,decision,llm.provider,autoresearch}` have no wheel equivalent → scripted/mirror paths; `02_autoresearch_loop` design-only | `vyapaar-agent` (research loop, llm adapters) / `vyapaar-ffi` | open |
| 0003 | `0003-vyapaar-data-nav-loaders` | `honba_data.loaders.{nse,yfinance}`, `store.mutual_funds`, `store.coverage` missing → in-repo `amfi.py`/loader shims; `honba.screener.{store,service}` bar-store surface missing | `vyapaar-data` | open |
| 0004 | `0004-vyapaar-wheel-display-universes-client` | `honba.display`, `honba.markets.india.universes`, `honba.client`, `honba.cli.data` missing → mirrors in `display_style.py` / `universe_lists.py` | `vyapaar-ffi` | open |
| 0005 | `0005-vyapaar-exec-freeze-slicer-mirror` | freeze-limit auto-slicing only mirrored (Stage 6); wheel `Sizer` cannot slice | `vyapaar-exec` (freeze slicer crate) / `vyapaar-ffi` | reserved (Stage 6) |

Status values: `reserved` (numbering held, not yet filed) · `open` (mirror/stub
is live in this repo; filing doc exists or lands with the referencing stage) ·
`closed` (owner shipped; delete the file with the mirror's removal — see the
closing commit).

Per gap doc template: status · what is stubbed/mirrored · why · how to close it.
