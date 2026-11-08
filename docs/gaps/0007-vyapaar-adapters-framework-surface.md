# 0007 — vyapaar-adapters-framework-surface

**Status**: open
**Owning repo**: `vyapaar-adapters` (broker connector packages advertised through the
adapters entry-point group) / `vyapaar-ffi` (compiled `vyapaar` wheel exposing the
`vyapaar.adapters` framework namespace).

## Symptom
The adapter framework that `basic`/`candles` stage-2 scripts drive — the contract suite,
registry, capability declarations, canonical result models, `FakeAdapter` test double,
session/rate-limit/secrets plumbing — lives only in the source engine (`honba.adapters`).
The `vyapaar` wheel exposes no `vyapaar.adapters` namespace, and no `honba.client`
(REST/native ABI client) mirror exists, so `adapters/rest.py` and `adapters/gateway.py`
cannot be compiled against any target surface at all.

## What stands in (mirror)
`vyapaar_examples/_kernel/adapters/` — verbatim mirror of the source adapters framework,
retargeted to `_kernel.*` imports (13 modules): `base` (lifecycle façade +
`MarketDataAdapter`/`ExecutionAdapter` role protocols, ADR 0010), `models`, `errors`,
`capabilities`, `registry` (entry-point group constant renamed `vyapaar.adapters`),
`contract` (async conformance suite), `testing` (`FakeAdapter`), `session`, `rate_limit`,
`secrets`, `boundary`, `order_events`.

**Excluded**: `rest.py` and `gateway.py` — both import `honba.client` (the HTTP/native
API client, part of the gap 0004 wheel surface), which no `vyapaar` equivalent provides
yet. Nothing in stage 2–4 consumers needs them; add them back when the client surface
exists.

Broker implementations are *not* mirrored: they live in the separate `vyapaar-adapters`
repository as packages advertising through the (renamed) entry-point group, exactly as the
source repo intends the boundary to work. `examples/basic/README.md` links the sibling
`../../../vyapaar-adapters/examples/` checkout.

## Why
Stage 2 of the staged port (`docs/plans/0002-honba-examples-staged-port.md`) ports the
`basic` (5) and `candles` (4) topics, whose whole subject is the adapter façade: registry
resolution, capability refusals-as-data, intents → reports → fills over `FakeAdapter`,
idempotent repeats, and the capability conformance contract. The contract suite is itself
asserted by ported tests, so a behavioral stand-in is required, not a stub.

## How to close
Ship the adapters framework through `vyapaar-ffi` (`vyapaar.adapters`) — or a dedicated
wheel namespace — keeping the same public names (`Adapter`, `ExecutionAdapter`,
`MarketDataAdapter`, `resolve_adapter`, `available_adapters`, `FakeAdapter`, error/capability
types). Then delete `_kernel/adapters/`, retarget the scripts' imports, and drop the
`rest.py`/`gateway.py` exclusion once `honba.client`'s equivalent (`vyapaar.client`, gap
0004) also ships.
