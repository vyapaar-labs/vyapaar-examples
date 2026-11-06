# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Tier 6D (COMPLETE)**: Reference Learning Path implemented from the
  sub-guide contracts (source `honba-examples` unavailable; implemented fresh).
* **Fincept/Quantcept Layer 6 (COMPLETE)**: `docs/plans/0001` implemented —
  examples `12_portfolio_allocation` (`vyapaar-ledger-allocation` mirror:
  mean-variance tangency, damped risk parity, clip-and-renormalize bounds),
  `13_black_scholes_greeks` (`vyapaar-market-pricing` mirror: BS price, five
  Greeks, IV bisection; documented `f64`-internal/`Decimal`-boundary
  exception), `14_timeseries_forecast` (`vyapaar-agent-forecast` Theta mirror),
  `15_fama_macbeth_factor_regression` (`vyapaar-agent-panel` mirror). Shared
  exact-`Decimal` stats/linear-algebra in `vyapaar_examples/quant.py`
  (`returns`, `mean`, `std_dev`, `covariance_matrix`, `solve_linear_system`,
  `ols`). Gate: 21 tests, `ruff check`, `ruff format --check`, and
  `mypy vyapaar_examples` all PASS.

## Decisions & Discoveries
* pyproject: removed `rust_decimal`; declared `vyapaar`, `vyapaar-strategies`,
  `vyapaar-data`, `polars`, `pydantic`.
* Digit-named example modules (`01_loading_data.py`) cannot use `import`;
  tests load them via `importlib.util.spec_from_file_location`.
* Zero floats start at the source: synthetic walks step in integer paise and
  materialize `Decimal`; ruff RUF032 forbids `Decimal(<float literal>)`.
* RUF002 is live (ambiguous-unicode lint): docstrings keep Greek/Unicode
  math out except where the existing examples already use them; new example
  docstrings prefer ASCII math.
* mypy `exclude` patterns are substring-matching: CI type-checks only
  `vyapaar_examples`; example/tests modules are not mypy-clean by design.
* Black-Scholes (example 13) mirrors the pricing crate's documented exception:
  `math` floats internally, `Decimal` rounded to 8dp at the boundary.
* Examples run standalone with the package installed (or `PYTHONPATH=.`);
  pytest resolves `vyapaar_examples` via the rootdir `conftest.py`.

## Immediate Next Step
* None in this repo. Add a runnable example for any *future* shipped engine
  per `docs/plans/0001` (its Phase 1 now says exactly that).

## Operating Invariants
* Zero floats in financial math (one documented exception: BS internals in
  example 13); examples deterministic and offline; tests live in `tests/` only.
