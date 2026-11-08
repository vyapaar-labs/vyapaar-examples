# 0005 — vyapaar-exec-freeze-slicer-mirror

**Status**: open
**Owning repo**: `vyapaar-exec` (freeze slicer crate) / `vyapaar-ffi` (wheel
`Sizer` surface).

## Symptom
There is no real `vyapaar-exec` freeze-limit auto-slicer package, and the
wheel's `Sizer` type cannot slice an order against a freeze limit.

## What stands in
`vyapaar_examples/options/__init__.py`'s `freeze_limit_qty()` / `slice_order()`
/ `verify_slices()` (already landed in Stage 1) stand in for the real crate.
`examples/options/07_large_qty_options_slicer.py` and
`examples/stocksharp/02_twap_vwap.py` (the latter lands in a separate
subagent's task, same gap) both probe for an optional `vyapaar_te_slicer`
package and fall back to this same local mirror when it's absent (which it
always is today).

## How to close
Once `vyapaar-exec`/`vyapaar-ffi` ship a real slicer surface, delete the local
mirror in `vyapaar_examples/options/__init__.py` and retarget both scripts'
imports to the real package.
