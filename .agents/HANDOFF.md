# `vyapaar-examples` — Inter-Agent Handoff

## Phase / Slice Status
* **Tier 6D (COMPLETE, superseded scope note)**: Reference Learning Path
  (flat `examples/01`–`15` + 8-module harness) implemented fresh. The claimed
  "source `honba-examples` unavailable" no longer holds: the source checkout
  is at `/home/pmallapp/Devel/Finance/honba-workspace/honba-examples` and is
  NOT ported (94 topic scripts + 13 topic READMEs + 54 harness modules +
  103 unit/5 integration tests + 2 snapshot goldens + 6 docs).
* **Honba staged port (IN PROGRESS — Stage 0 complete)**:
  `docs/plans/0002-honba-examples-staged-port.md` — 9 stages (0 pre-flight →
  8 docs/index sweep), rename/retarget map (D1–D9), overlap policy: fresh
  `backtest.py`/`metrics.py` stay canonical, source capabilities get grafted.
  * **Stage 0 (pre-flight) DONE** on `feat/port-stage-0-preflight`: pyproject
    adds `vyapaar-adapters` dep + optional extras `ai`/`optimizer`
    (optuna+scipy+matplotlib), `mutual-funds` (scipy), `screening` (duckdb),
    dev `hypothesis`; `docs/gaps/README.md` created reserving `0001`–`0005`
    numbering; gate `pytest -q && ruff check . && ruff format --check . &&
    mypy vyapaar_examples` green. Remaining stages 1–8 not started.
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
* pyproject: removed `rust_decimal`; declared `vyapaar`, `vyapaar-adapters`
  (Stage 0), `vyapaar-strategies`, `vyapaar-data`, `polars`, `pydantic`.
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
* Dev-venv state (Stage 0 probe): **the `vyapaar` wheel is absent locally** —
  `python -c "import vyapaar"` → `ModuleNotFoundError`; no repo venv; system
  python is PEP-668 externally-managed and optuna could not be installed into
  it (only missing optional dep; scipy/matplotlib/duckdb/hypothesis are
  importable). Consequence: every wheel-touching ported module must keep
  passing via `vyapaar_examples._compat` fallbacks; optuna-gated tests use
  lazy import / `pytest.importorskip` (D7).
* Examples run standalone with the package installed (or `PYTHONPATH=.`);
  pytest resolves `vyapaar_examples` via the rootdir `conftest.py`.

## Immediate Next Step
* Execute **Stage 1 (shared harness port)** of
  `docs/plans/0002-honba-examples-staged-port.md` on branch
  `feat/port-stage-1-harness-staged-port` (rebased on Stage 0): port the
  source `~44` harness modules (verbatim after D4/D5), graft source
  `backtest.py`/`metrics.py` into the fresh canonical modules, port the
  ~40 harness unit tests + `tests/unit/conftest.py`, rename
  `HonbaExample` → `VyapaarExample`, file gaps `0001`–`0004` docs beside
  their mirrors, gate
  `pytest -q tests/unit -k "pipeline or screening or ewr or sip or settlement
  or catalog or amfi"` plus the full `pytest -q && ruff check . &&
  ruff format --check . && mypy vyapaar_examples`.

## Operating Invariants
* Zero floats in financial math (one documented exception: BS internals in
  example 13); examples deterministic and offline; tests live in `tests/` only.
* Ported topic scripts keep source file names verbatim, topic-relative slots
  never reused (`ai_research/08` reserved); flat `01`–`15` journey untouched.
