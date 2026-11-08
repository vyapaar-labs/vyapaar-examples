# 0002 — Staged Port: `honba-examples` → `vyapaar-examples`

> **Status**: **In progress** — Stage 0 (pre-flight), Stage 1 (shared harness),
> Stage 2 (SDK fundamentals: `basic` 5, `candles` 4, `strategies` 16) and Stage 3
> (tester & enhancer: `backtesting` 11, `optimizer` 3) are done; Stages 0-2 landed on
> `main` (stacked branches `feat/port-stage-0-preflight` →
> `feat/port-stage-1-harness-staged-port` → `feat/port-stage-2-sdk-fundamentals`).
> Gates green after Stage 3: `pytest` 509 passed / 110 skipped, `ruff check`,
> `ruff format --check`, `mypy vyapaar_examples` (222 files), stage filter 45 passed /
> 2 skipped. Gaps `0001`–`0004`, `0006`–`0008` filed (`0005` reserved for Stage 5).
> Remaining: Stage 4 (lakehouse consumers) onward.
> **Source**: `/home/pmallapp/Devel/Finance/honba-workspace/honba-examples`
> **Target**: `/home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples`
> **Context correction**: `docs/migration-guide.md` and `.agents/HANDOFF.md` assert the
> learning path was "implemented fresh because source `honba-examples` unavailable". The
> source checkout **is now present** in the workspace; virtually none of it is ported yet.
> This plan supersedes the flat "copy `src/honba_examples/*` → `vyapaar_examples/*`"
> step in `docs/roadmap/roadmap.md` and stages the real port.
> **Depends on reading**:
> - `vyapaar-examples/README.md` (4-Zone layout + invariants)
> - `/home/pmallapp/Devel/Finance/honba-workspace/honba-examples/plan.md` (source repo master plan)
> - `docs/plans/0001-fincept-gap-closing-examples.md` (repo plan conventions)

---

## 0. Executive Summary

`vyapaar-examples` currently holds only a **fresh-written entry journey**: 15 flat scripts
(`examples/01_loading_data.py` … `15_fama_macbeth_factor_regression.py`), an ~720-LOC
shared harness (`vyapaar_examples/`: data, metrics, backtest, walkforward, sdk, fake_llm,
quant, _compat) and 17 test modules.

The source repository is far larger and none of it is here:

| Artifact | Source count | Ported today |
| :--- | ---: | ---: |
| Example scripts (`examples/<topic>/NN_*.py`) | 94 numbered + 1 shared module, across 13 topics | 0 |
| Topic `README.md` files | 13 | 0 |
| Shared library modules (`src/honba_examples/**`) | 54 | ~6 concepts re-implemented fresh |
| Unit test modules (`tests/unit/test_*.py`) | 103 (+ conftest, __init__) | 17 (fresh) |
| Integration tests (`tests/integration/test_*.py`) | 5 | 0 |
| Snapshot goldens (`tests/snapshots/`) | 2 (`backtest_parity_golden.json`, `output_report.txt`) | 0 |
| Concept docs (`docs/*.md`) | 6 | 0 |

The port is staged so that every stage keeps the repo green (`pytest -q`, `ruff check .`,
`ruff format --check .`, `mypy vyapaar_examples`), never touches the 15 existing numbered
scripts, and lands as a separate `feat/port-stage-N-<slug>` PR.

The **existing fresh code is treated as canonical wherever names collide** (see Decision
D3): ported source modules are grafted in, not pasted over.

---

## 1. Current-State Delta (probe-verified)

### 1.1 Source inventory (honba-workspace/honba-examples)

- `examples/` — 13 topic directories, 95 `.py` files total:
  `basic` (5) · `candles` (4) · `strategies` (16) · `backtesting` (11) · `storage` (4) ·
  `universes` (10: `01`–`09` + shared `alpha30_constituents.py`) · `screening` (8) ·
  `options` (8) · `stocksharp` (5) · `optimizer` (3) · `mutual_funds` (4) ·
  `ai_research` (11: `01`–`07`, `09`, `10`–`12`; **slot `08` stays reserved**) ·
  `production` (6). Every topic has its own `README.md`; `examples/README.md` indexes all.
- `src/honba_examples/` — 54 modules: 21 top-level (`base`, `output`, `jsonable`,
  `artifact`, `bars`, `catalog`, `cli`, `decision_guard`, `display_style`, `screener_cli`,
  `settlement`, `synthetic`, `universe_lists`, `amfi`, `replay_report`, `sip`, `sip_plan`,
  `sip_report`, `backtest`, `metrics`, `__init__`) and 4 subpackages with 33 modules:
  `pipeline/` (11), `screening/` (14), `ewr/` (6), plus `ai_replay/`, `optimizer/`,
  `options/` (1 module each).
- `tests/` — 103 unit test modules + `conftest.py` (synthetic NSE parquet catalog +
  fundamentals fixtures built on `duckdb`), 5 integration tests, 2 snapshot goldens.
  Includes `test_pitfalls_sections.py` (docstring-contract enforcement),
  `test_metrics_property.py` (hypothesis), `test_polyrepo_decoupling.py`.
- `docs/` — 6 notes: `dsr_pbo.md`, `wfo_efficiency.md`, `options_microstructure.md`,
  `multibagger_screening_research.md`, `refactor-plan.md`, `roadmap-chaining.md`.
- `pyproject.toml` — `requires-python >= 3.12`; base dep `honba`; extras
  `dev` (pytest, ruff, hypothesis, pyright), `mutual-funds` (honba-data, scipy),
  `optimizer` (optuna, scipy, matplotlib), `ai` (optuna, scipy); src layout.

### 1.2 Target inventory (vyapaar-labs/vyapaar-examples)

- 15 flat numbered scripts + 8-module harness (`backtest`, `_compat`, `data`, `fake_llm`,
  `metrics`, `quant`, `sdk`, `walkforward` — `__init__` re-exports
  `SMA/RSI/Bar/Cache…`-style public names, `ScriptedFakeLlm`, `Backtest*`,
  `walk_forward_*`).
- `pyproject.toml`: `requires-python >= 3.11`; deps `vyapaar`, `vyapaar-strategies`,
  `vyapaar-data`, `polars`, `pydantic`; dev extras pytest/ruff/mypy; flat package (no
  `src/` layout); pytest `-q` testpaths `tests`; ruff `E,F,I,UP,B,SIM,RUF`, line 100,
  py311; mypy checks only `vyapaar_examples`.
- Known lint constraints (from HANDOFF): digit-named files load tests via
  `importlib.util.spec_from_file_location`; RUF032 forbids `Decimal(<float>)`; RUF002
  live; zero-float financial math (one documented exception: example 13 BS internals).

### 1.3 Dependency surfaces (what the port can already rely on)

- **`vyapaar` wheel** (vyapaar-ffi, `python/vyapaar/__init__.pyi`): `Price`, `Quantity`,
  `Currency`, `Exchange`, `InstrumentId`, `OrderSide`, `TimeInForce`, `OrderStatus`,
  `DepthLevel`, `Bar`, `Tick`, `OrderRequest`, `OrderAck`, `FillReport`, `OrderEvent`,
  `Decision`, `RiskEngine`, `StrategyRunner`, `Parameter`, `Strategy` (`buy`/`sell`/`on_*`),
  `run(strategy, bars, algo_id) → BacktestResult`, `to_decimal`, `instrument_id`,
  `Sizer` + `fixed_quantity`/`fractional`/`risk_budget`, `Session`/`current_session`/
  `is_live` (IST windows), `SMA/EMA/RSI`, `bars_to_stream`/`ticks_to_stream`/
  `stream_capsule_name` (Arrow), `now_iso`.
  **Not on the wheel** (needed by ported examples): `algo_analytics`
  (walk_forward/folds/monte_carlo/deflated_sharpe), `ai.*`
  (ask/decision/llm.provider/autoresearch), `display`, `client`, `cli.data`,
  `markets.india.universes`, a full `backtest.simulated`-class engine (costs, latency,
  fills) — only the toy `run()`.
- **`vyapaar_data`**: `adapters/parquet_catalog.py`, `adapters/duckdb_store.py`,
  `cli/coverage.py` (`__main__`), `domain/` (corporate_actions, coverage, fundamentals),
  `ports/repositories.py`, `providers/bhavcopy.py`, `service/data_service.py`.
  **Not present**: `loaders/nse`/`yfinance` point-in-time loaders, `store.mutual_funds`
  (AMFI NAV store), `store.coverage`.
- **`vyapaar_adapters`**: `dhan`, `zerodha`, `angelone`, `upstox`, `fyers`, `kotak`,
  `iifl`, `paper`, `registry.py` (+ entry-point group `vyapaar.adapters`), `common/`.
  **Not verified**: `honba.adapters.testing`-equivalent fixtures.
- **`vyapaar_strategies`**: `catalog/`, `manifests/`, `schema/` — replaces
  `--strategies-dir ../honba-strategies` lookups.

---

## 2. Global Port Conventions (Decisions)

- **D1 — Layout**. New scripts land as `examples/<topic>/NN_<name>.py` with the source
  file name preserved **verbatim** (renames only, D4). The flat 01–15 entry journey stays
  untouched — no renumbering, no test renames. Topic numbering is topic-relative; number
  slots are never reused or shifted; `ai_research/08` remains reserved.
- **D2 — Zoned harness home**. `src/honba_examples/X*` → flat `vyapaar_examples/X*`.
  Subpackages keep their names: `ai_replay/`, `ewr/`, `optimizer/`, `options/`,
  `pipeline/`, `screening/`. `tests/unit|integration|snapshots` keep the same structure.
- **D3 — Overlap policy**. The fresh files `backtest.py` and `metrics.py` are canonical
  for their names: **graft** missing source capabilities into them (keeping the fresh
  public API + existing 17 tests green), while their ported source tests are adapted to
  the grafted API. Fresh modules with no source counterpart (`_compat`, `data`, `sdk`,
  `fake_llm`, `quant`, `walkforward`) stay; ported examples call them where the fresh
  implementation already covers the need. Source `synthetic.py` and `data.py` overlap →
  consolidate into `data.py` unless source semantics differ materially (then port both and
  re-export). Never keep two implementations of the same math.
- **D4 — Rename map** (sed-level, applied to every ported file):
  `honba_examples` → `vyapaar_examples`; `honba` → `vyapaar`;
  `HonbaExample` → `VyapaarExample`; `HONBA_…` env vars (`HONBA_STRATEGIES_DIR`) →
  `VYAAPAAR_…`; prose "Honba" → "Vyapaar"; drop the Japanese 本場; license header
  "Honba Labs" → "Vyapaar Labs".
- **D5 — Module-level import retargets** (mirror of §1.3):
  `honba.domain.*` → wheel types (`Bar`, `Tick`, `InstrumentId`, `OrderSide`, …);
  `honba.backtest.simulated` → grafted `vyapaar_examples.backtest` (mirror semantics);
  `honba.algo_analytics.*` → `vyapaar_examples.optimizer` + `quant.py` mirrors (gap
  `0001`); `honba.ai.*` → `vyapaar_examples` scripted/mirror paths + `vyapaar-agent-mcp`
  for MCP (gap `0002`); `honba_data.*` → `vyapaar_data.*`; `honba_data.loaders.nse /
  yfinance` and `store.mutual_funds` → in-repo `amfi.py` + gap `0003`;
  `honba.(adapters ↔) honba_adapters.*` → `vyapaar_adapters.*`; catalog strategies →
  `vyapaar_strategies` catalog; `honba.markets.india.universes` → `universe_lists.py`
  mirror (gap `0004`).
- **D6 — Python 3.11 target**. Source is 3.12; after D4 renames, ported files must be
  3.11-clean (no PEP-695 `type` statements and similar) and ruff `E,F,I,UP,B,SIM,RUF`-
  clean (notes: RUF002 ASCII-only docstrings in new text; RUF032 — never build a
  `Decimal` from a float literal; synthetic prices must step in integer paise as the
  fresh examples do).
- **D7 — Offline & deterministic gate (inherits source principle 6)**. Every ported
  script still runs offline on synthetic/fixture data with `ScriptedFakeLlm`. Optional
  deps (optuna, scipy, matplotlib, duckdb) become `pyproject.toml` optional-dependencies;
  scripts lazy-import and degrade gracefully; their tests `pytest.importorskip` so CI
  never needs them.
- **D8 — Docstring contracts preserved**. `Pitfalls::` sections are ported as-is and the
  ported `test_pitfalls_sections.py` extends coverage to `examples/<topic>/**` plus the
  flat 01–15 scripts. "Rates read from the cost model / instrument master, never
  hard-coded" is an invariant of every derivative/settlement example.
- **D9 — Index & docs handled by Stage 8**, but a topic's README row is added **in the
  same PR** that ports that topic (source convention), not deferred silently.

---

## 3. Staged Execution Plan

Each stage is: **(a)** port code + **(b)** port/adapt its tests + **(c)** update the topic
README row in the same PR + **(d)** file the listed gaps (§4) + **(e)** update
`.agents/HANDOFF.md` in the same change. Exit gate per stage: `pytest -q && ruff check .
&& ruff format --check . && mypy vyapaar_examples` plus any stage-specific verification.

### Stage 0 — Pre-flight (no feature code)

1. `pyproject.toml`: add `vyapaar-adapters>=0.1.0` to deps; add optional-dependencies
   `optimizer`/`ai` (optuna, scipy, matplotlib), `mutual-funds` (scipy), `screening`
   (duckdb — transitively via vyapaar-data), `dev` gets `hypothesis`.
2. Reserve `docs/gaps/` numbering per §4.
3. Verify the wheel import works in the dev venv (`python -c "import vyapaar"`); if the
   wheel is absent locally, all wheel-touching ports must still pass via `vyapaar_examples._compat`
   fallbacks — record venv state in HANDOFF.
**Gate**: `pytest -q` green on untouched tree + new extras installed.

### Stage 1 — Shared harness (`vyapaar_examples`, ~54 → ~50 files)

1. Port verbatim (after D4/D5): `base`, `output`, `jsonable`, `artifact`, `bars`,
   `catalog`, `cli`, `decision_guard`, `display_style`, `screener_cli`, `settlement`,
   `universe_lists`, `amfi`, `replay_report`, `sip`, `sip_plan`, `sip_report` +
   subpackages `ai_replay/`, `optimizer/`, `options/`, `ewr/` (6), `pipeline/` (11),
   `screening/` (14).
2. Graft source `backtest.py` (cost/latency model, simulated fills) and `metrics.py`
   capabilities into the fresh modules (D3). Port source `synthetic.py` decision via D3.
3. Port tests: the ~40 harness unit tests (test_base, test_output, test_jsonable,
   test_artifact, test_bars, test_catalog, test_cli, test_decision_guard,
   test_settlement, test_universe_lists, test_amfi(+loader), test_replay_report,
   test_sip_helpers/plan/simulation, test_synthetic, test_ewr_simulation, test_pipeline*,
   test_screening_*, test_nl_support, …) + `tests/unit/conftest.py` fixtures.
4. Class rename: `HonbaExample` → `VyapaarExample` (docstrings keep the "base class for
   examples" wording).
**Stage verification**: `pytest -q tests/unit -k "pipeline or screening or ewr or sip or
settlement or catalog or amfi"`.

### Stage 2 — SDK fundamentals (`basic` 5, `candles` 4, `strategies` 16)

Strategy/topic scripts move onto the wheel surface (`Strategy`, `Parameter`, wheel
`SMA/EMA/RSI` vs fresh `sdk.py` mirrors — mirror the pattern `01`–`15` already use) and
`vyapaar_adapters.registry` for connect/subscribe/paper-order/positions flows. Ported
scripts keep `--adapter fake` offline default. Attention: statutory-cost examples
(`strategies/03`, `04`, `13`) must read rates from the grafted cost model (Stage 1), not
hard-code. Tests: port the ~25 corresponding `test_NN_*.py` files slot-for-slot.
**Stage verification**: `pytest -q tests/unit -k "connect_dhan or fetch_instruments or
subscribe_quotes or place_order or check_positions or first_strategy or with_indicators
or position_sizing or risk_management or multi_instrument or bracket_order or
partial_fill or lifecycle"`.

### Stage 3 — Tester & enhancer (`backtesting` 11, `optimizer` 3)

Backtester mirrors (costs, latency, Monte-Carlo permutation, sweep/concurrent runs) live
on the grafted `backtest.py`; WFO/DSR/PBO on `optimizer/` + `quant.py`. GA/TPE scripts
come from source as pure-Python mirrors of `vyapaar-runtime`'s Strategy Optimizer
(crates GA/Bayesian/WFO/DSR); grade the mirrors against the source notes
`dsr_pbo.md` and `wfo_efficiency.md` (ported into `docs/reference/` in this same stage).
Optional deps paths (D7).
**Stage verification**: `pytest -q tests/unit -k "backtest or walk_forward or monte_carlo
or gaussian or deflated_sharpe"` + golden parity `tests/snapshots/backtest_parity_golden.json`
ported and byte-compared after rename.

### Stage 4 — Lakehouse consumers (`storage` 4, `universes` 10, `mutual_funds` 4)

Point-in-time loading via `vyapaar_data` (`parquet_catalog`, `duckdb_store`, `service`,
`providers/bhavcopy`, `domain/*`). In-repo loaders fill the `vyapaar_data` holes
(`amfi.py` for NAV; gap `0003` records the missing `store.mutual_funds`/loaders surface).
Universes: `universe_lists.py` (NIFTY50/BANKNIFTY/Alpha30) + `ewr/` scheduling/sizing and
`alpha30_constituents.py`. Optional deps: scipy (D7).
**Stage verification**: `pytest -q tests/unit -k "parquet or bhavcopy or amfi or nav or
universe or alpha30"`.

### Stage 5 — Screeners (`screening` 8)

`pipeline/` + `screening/` (already ported in Stage 1) power
`01_multibagger…08_swing_ap_setup` incl. chains (`06_run_chain`, chain TOMLs), `screener_cli`
and `screening/dispatch`. Port `docs/multibagger_screening_research.md` in this stage.
Tests incl. `test_run_chain`, `test_pipeline_chaining`, snapshot `output_report.txt`.
**Stage verification**: `pytest -q tests/unit -k "screener or chain or screening"`.

### Stage 6 — Derivatives & StockSharp (`options` 8, `stocksharp` 5)

Options (chain, Greeks mirror on `quant.py`, straddle/iron-condor/expiry-day, 9:20
straddle, freeze-limit slicer — mirror of `vyapaar-exec` freeze slicing; rates from the
cost model per D8; gap `0005`) and the five ported StockSharp reference strategies
(pairs, TWAP/VWAP, turtle, market-maker, risk-parity — listing which have catalog
counterparts in `vyapaar_strategies/catalog`). scipy needed for cointegration (D7).
**Stage verification**: `pytest -q tests/unit -k "greek or straddle or iron_condor or
expiry or slicer or pairs or twap or turtle or market_maker or risk_parity"`.

### Stage 7 — AI research & production (`ai_research` 11, `production` 6)

- `decision_guard` (Stage 1) clamps scripts through the wheel `Decision` + `RiskEngine`
  grammar (NoFX §5.5: untrusted-AI invariants, `deny_unknown_fields` semantics).
- `ai_replay/` + `replay_report` port the SHA-256 prompt-cache cassettes (11, 12).
- `10_claude_autonomous_quant` targets the `vyapaar-agent-mcp` server (agent repo;
  migration complete per its `docs/migration-guide.md`) with `ScriptedFakeLlm` default.
- `02_autoresearch_loop` — **carry-over gap in the source itself** ("blocked on
  `honba.ai.autoresearch` stubs; 0-byte today"): port as design-only with an explicit
  `pytest.skip` + gap `0002` (owner: `vyapaar-agent` autonomous research loop + wheel).
- Production scripts (`paper`, `live (Dhan)`, `multi_account`, `monitoring`,
  `deployment`, `06_multi_broker_dispatch`) run on `vyapaar_adapters` registry
  (`paper.py`, `dhan.py`, entry points) with offline defaults; live credentials only
  behind explicit flags. Gap `0004` covers missing wheel `display`/`client` surfaces any
  of these reach.
**Stage verification**: `pytest -q tests/unit -k "typed_llm or autonomous or replay or
mcp or paper or multi_account or dispatch"`.

### Stage 8 — Docs, index, suite sweep (closing)

1. Port topic READMEs (13) and remaining concept docs into `docs/reference/`
   (`refactor-plan.md`, `roadmap-chaining.md`, plus whatever earlier stages did not
   relocate), and create the `examples/README.md` index merged from the 13 topic tables.
2. Port `tests/snapshots/*`, `test_polyrepo_decoupling.py`, the `test_pitfalls_sections.py`
   scope-extension to topic dirs, and remaining `test_*.py` not already ported.
3. Sweep gates: `grep -ri honba examples vyapaar_examples tests` must return **only**
   prose mentions of the port provenance — no identifiers, no imports.
4. Update `docs/roadmap/roadmap.md` milestones to closed, `docs/migration-guide.md` §2
   to the executed pipeline, and archive this plan's status line to **Implemented**.
**Final gate** (full CI equivalent): `pytest -q && ruff check . && ruff format --check .
&& mypy vyapaar_examples && make check`.

### Explicit non-goals

- No renumbering or deletion of the fresh 01–15 entry journey; `0001`'s example-per-shipped-
  engine rule still governs *future* engines.
- No new engine capability in this repo (Tier 6D stays a learning path; mirrors only
  mirror Rust crates' public semantics).
- No live-credential runs in tests; adapters stay `fake`/`paper` in CI.

---

## 4. Gaps To File While Porting (per workspace gap-tracking rule §9)

Create `docs/gaps/README.md` on first filing; numbers below are the reserved order
(renumber if others land first). Each gap names the owning repo so a later wheel/data
change closes it here by deleting the mirror.

| # | Slug | Symptom in this repo | Owning repo / path |
| :--- | :--- | :--- | :--- |
| 1 | `0001-vyapaar-wheel-algo-analytics-surface` | `honba.algo_analytics.{walk_forward,folds,monte_carlo,deflated_sharpe}` missing from the `vyapaar` wheel → `vyapaar_examples/optimizer` + `quant.py` mirrors | `vyapaar-runtime` (enhancer crates) / `vyapaar-ffi` (wheel surface) |
| 2 | `0002-vyapaar-wheel-ai-provider-surface` | `honba.ai.{ask,decision,llm.provider,autoresearch}` missing → scripted/mirror paths; `02_autoresearch_loop` design-only | `vyapaar-agent` (research loop, llm adapters) / `vyapaar-ffi` |
| 3 | `0003-vyapaar-data-nav-loaders` | `honba_data.loaders.{nse,yfinance}`, `store.mutual_funds`, `store.coverage` missing → in-repo `amfi.py`/loader shims | `vyapaar-data` |
| 4 | `0004-vyapaar-wheel-display-universes-client` | `honba.display`, `honba.markets.india.universes`, `honba.client`, `honba.cli.data` missing → mirror in `universe_lists.py`/`display_style.py` | `vyapaar-ffi` |
| 5 | `0005-vyapaar-exec-freeze-slicer-mirror` | freeze-limit auto-slicing only mirrored; wheel `Sizer` can't slice | `vyapaar-exec` (freeze slicer crate) / `vyapaar-ffi` |

Cite the gap number in a code comment at every workaround and in the stage's commit
message.

---

## 5. Sequencing & Rollback Rules

- Stages are strictly sequential (0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8): later ports depend
  on the grafted harness (Stage 1) and the tester mirrors (Stage 3).
- One PR per stage, branch `feat/port-stage-N-<slug>`, commit
  `feat(examples): port stage N (<scope>)`; HANDOFF's *Immediate Next Step* always points
  at the next unstarted stage.
- If a stage stalls mid-port, HANDOFF lists the exact last ported file + first test to
  adapt; partially-porting a topic (some scripts) is allowed only with the slot-unused
  rule (D1) intact and its README noting the missing rows.
