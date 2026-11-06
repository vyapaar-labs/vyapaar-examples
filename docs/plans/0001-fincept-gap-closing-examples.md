# 0001 — Example Notebooks for Fincept-Gap-Closing Features (Deferred)

> **Status**: Proposed — not yet implemented.
> **Target Crates**: `vyapaar-examples` (Python reference scripts/tutorials)
> **Depends on reading**:
> - (none external)

---

## 0. Executive Summary & Objective

This repo is out of scope for the current Fincept/Quantcepts gap-closing initiative. It is a learning-path/tutorial repo — "Runnable Python reference scripts for Indian equities, options, factor models, and backtesting" per its own `AGENTS.md` — not a place where new engine capability gets built.

---

## 1. Context

Other planning docs in this initiative propose new engine capability elsewhere in the workspace (e.g. a portfolio-optimizer allocation engine in `vyapaar-ledger`, an options-Greeks pricing crate in `vyapaar-market`, and potentially future volatility/regime/copula engines). None of that work belongs in this repo. This repo's only role in the initiative is downstream and deferred: once a new engine actually ships, add one runnable example demonstrating it.

---

## 2. Component Specifications

No component work is proposed now. The only forward-looking action item: once any new engine proposed elsewhere in this initiative actually ships (e.g. `vyapaar-ledger-allocation`'s portfolio optimizer, `vyapaar-market-pricing`'s options Greeks, any future volatility/regime/copula engine), add one runnable example notebook per shipped engine to this repo, demonstrating it against the existing example-data conventions this repo already uses — not before.

---

## 3. Implementation Phases

### Phase 1 (deferred, not started)
Revisit this doc once a first new engine from the wider initiative actually ships, and add its example then — do not pre-build examples for unshipped features.
