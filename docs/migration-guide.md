# `vyapaar-examples` — Migration & DDD Refactoring Guide

> **Tier**: Tier 6D
> **Source**: `/home/pmallapp/Devel/Finance/honba-workspace/honba-examples`
> **Target**: `/home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples`

---

## 1. Migration Status
The entry learning path (`examples/01`–`15`, 8-module harness) was implemented
fresh while the source was believed unavailable. The source checkout **is now
present**, so the full port proceeds as the **staged execution plan in
`docs/plans/0002-honba-examples-staged-port.md`** (Stages 0–8; rename/retarget
map and reserved gap docs inside). The earlier flat "copy `src/honba_examples/*`
→ `vyapaar_examples/*`, `examples/*` → `examples/`, `tests/*` → `tests/`"
step is superseded by that plan — a straight copy would clobber the canonical
fresh `backtest.py`/`metrics.py` and the flat numbered scripts.

~~1. **Fix `pyproject.toml`** — remove invalid `rust_decimal`.~~ (Done.)

---

## 2. Verification Commands
```bash
cd /home/pmallapp/Devel/Finance/vyapaar-labs/vyapaar-examples
pytest -q
ruff check .
```
(Per-stage verification selectors and the final sweep gate are listed inside
plan `docs/plans/0002-honba-examples-staged-port.md` §3.)
