# 0002 — vyapaar-wheel-ai-provider-surface

**Status**: open
**Owning repo**: `vyapaar-agent` (autonomous research loop, LLM adapters, MCP server) and
`vyapaar-ffi` (wheel surface).

## Symptom
`honba.ai.{ask, decision, llm.provider, autoresearch}` have no `vyapaar` equivalent, so the
port cannot ship real LLM-backed flows offline or against the agent runtime.

## What stands in (scripted/mirror paths)
* `vyapaar_examples/fake_llm.py` — `LlmPort` + `ScriptedFakeLlm` (deterministic scripted
  provider used by every offline example).
* `vyapaar_examples/decision_guard.py` — kernel-verbatim decision grammar (approve /
  veto / size_down) so scripted LLM decisions flow through the same assertions the engine
  would enforce.
* `vyapaar_examples/screening/nl_support.py` — natural-language screener translation with a
  scripted provider fallback.
* `02_autoresearch_loop` remains design-only in the source repo and stays deferred; its
  tests skip until the `vyapaar-agent` loop ships (pytest.skip + this gap).

## How to close
Provide the wheel/agent surface (`vyapaar.ai.llm.provider`, decision parsing, MCP bridge —
`vyapaar-agent-mcp`), then delete `fake_llm.py`'s provider shim and retarget the D5 imports.
