# Vyapaar Examples (`vyapaar-examples`)

**Bounded Context**: Reference Learning Path (Tier 6D)

`vyapaar-examples` is the canonical educational journey for the Vyapaar Labs
ecosystem: numbered, deterministic, offline-runnable scripts covering Indian
equities, NSE/NFO options microstructure, factor models, walk-forward
optimization (WFO), and the autonomous AI research loop.

Examples **12–15** are the Fincept/Quantcept gap-closing set: one runnable
script per engine shipped in that initiative — `vyapaar-ledger-allocation`
(mean-variance & risk parity), `vyapaar-market-pricing` (Black-Scholes, Greeks,
implied volatility), `vyapaar-agent-forecast` (Theta), and `vyapaar-agent-panel`
(Fama-MacBeth). Each mirrors its Rust engine's public semantics in exact
`Decimal` so it stays deterministic and offline.

## Invariants

- **Offline & Deterministic by Default** — every example runs out of the box
  on synthetic/fixture data with a `ScriptedFakeLlm`; no live credentials, no
  network.
- **Strict Zero-Floats in Financial Math** — all prices, quantities, and fees
  are `decimal.Decimal`; synthetic prices are generated in integer paise.
- **Mandatory `Pitfalls::` Docstring Section** — every numbered script
  documents real-world Indian market pitfalls (STT traps, freeze limits, T+1
  settlement, look-ahead bias).
- **Every example has a regression test** — `tests/unit/test_<NN>_<name>.py`.

## Layout (4-Zone Clean Package)

```
vyapaar-examples/
├── vyapaar_examples/   # Zone 1: shared harness (data, metrics, backtest, WFO, fake LLM)
├── examples/           # Zone 2: numbered runnable scripts (01_.., 02_.., ...)
├── tests/              # Zone 3: per-example regression tests (tests/unit/)
└── docs/               # Zone 4: architecture & migration guides
```

## Run an Example

```bash
python examples/01_loading_data.py
```

## Development

```bash
make test      # pytest -q
make lint      # ruff check .
make check     # lint + format-check + type-check + tests
```

## Verification Gate

```bash
pytest -q
ruff check .
```
