# 0004 — vyapaar-wheel-display-universes-client

**Status**: open
**Owning repo**: `vyapaar-ffi` (wheel: `vyapaar.display`, `vyapaar.client`,
`vyapaar.markets.india.universes`, `vyapaar.cli.data`).

## Symptom
The wheel offers no display, universe, or client surface for the console output the
examples use.

## What stands in
* `vyapaar_examples/display_style.py` — console/table formatting mirror (Indian money
  grouping, table renderer), including the `format_money` graceful try-import of the
  future `vyapaar.utils.format` surface (comment cites this gap).
* `vyapaar_examples/universe_lists.py` — NIFTY50 / BANKNIFTY / Alpha30 universe mirrors
  (`resolve_universe`, constituents, `save_universe_history`).
* `vyapaar_examples/screener_cli.py` + `vyapaar_examples/stream.py` — output/stream
  plumbing the standalone CLIs print through.
* `vyapaar_examples/cli.py` — the base example CLI (out/format/width flags) replacing
  `honba.cli.data`.
* `vyapaar_examples/options/*` — instrument lookups via a best-effort
  `vyapaar.client.get_instrument` try-import (comment cites this gap).

## How to close
Ship the wheel display/universe/client modules; delete the mirrors and retarget the D5
imports (`from vyapaar.display → ...`, `from vyapaar.markets.india.universes → ...`).
