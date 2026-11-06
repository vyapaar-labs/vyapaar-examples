# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Tier 6D (COMPLETE)**: Implemented the Reference Learning Path from the
  sub-guide contracts (source `honba-examples` unavailable; implemented fresh).
* Package `vyapaar_examples/`: `data` (integer-paise deterministic synthetic
  bars + `trending_bars` + `SampleInstruments`), `sdk` (SMA/RSI/cross),
  `metrics` (`PerformanceMetrics`/`compute_metrics`, all-Decimal), `backtest`
  (bar-by-bar, cost-consistent round-trip PnL), `walkforward` (rolling
  train/validate windows), `fake_llm` (`ScriptedFakeLlm`).
* `examples/`: 11 numbered scripts (01 loading, 02 indicators, 03 order
  lifecycle, 04 bracket orders, 05 partial fills, 06 multi-symbol portfolio,
  07 turtle backtest, 08 NFO options microstructure, 09 Alpha30 factor model,
  10 walk-forward optimization, 11 autoresearch loop). Every script has a
  `Pitfalls::` docstring and a `main() -> dict` result contract.
* `tests/unit/`: one regression test per example plus `test_helpers.py`.

## Decisions & Discoveries
* pyproject: removed `rust_decimal`; declared `vyapaar`, `vyapaar-strategies`,
  `vyapaar-data`, `polars`, `pydantic`.
* Digit-named example modules (`01_loading_data.py`) cannot use `import`;
  tests load them via `importlib.util.spec_from_file_location`.
* Zero floats start at the source: synthetic walks step in integer paise and
  materialize `Decimal`; ruff RUF032 forbids `Decimal(<float literal>)`.
* mypy `exclude` patterns are substring-matching: `"examples"` excluded
  `vyapaar_examples`; removed the pattern (CI type-checks the package only).
* Backtest cost model: round-trip PnL = `(exit-entry)*qty - 2*cost*qty`,
  consistent with the cash ledger (cost charged on every delta trade).

## Immediate Next Step
* Tier 6E: `vyapaar-docs` — add CI workflow (`mkdocs build --strict`), then
  update the root superproject (submodule pointers + migration guide).

## Operating Invariants
* Zero floats in financial math; examples deterministic and offline; tests
  live in `tests/` only.
