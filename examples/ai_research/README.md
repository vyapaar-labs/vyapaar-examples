# 09 AI Research – the research loop on top of Vyapaar

The AI-research examples show the research loop layered on Vyapaar: natural-language
query → validated filter, autonomous backtesting, NL→strategy verification,
reinforcement learning, and the MCP tool gateway. There is no trading strategy
here. Six steps are runnable offline and deterministic (`ScriptedFakeLlm`, no
network, no API keys); the other four are documented design placeholders whose
modules exist in `vyapaar-agent` as stubs waiting for future roadmap phases (gap 0002).

## At a glance

| #  | File                              | Strategy / focus | What you learn / what it would do                                                                  |
|----|-----------------------------------|------------------|----------------------------------------------------------------------------------------------------|
| 01 | `01_llm_research_analyst.py`      | —                | **Runnable.** NL question → validated screener filter via `ScriptedFakeLlm` + `KnowledgePack`      |
| 02 | `02_autoresearch_loop.py`         | —                | **Design only.** `ResearchLoop` → generate hypotheses → backtest → journal (Faiss + Parquet)       |
| 03 | `03_nl_screener.py`               | —                | **Runnable.** NL query → strict screener filter → historical backtest                               |
| 04 | `04_nl_to_strategy.py`            | —                | **Design only.** NL description → strategy manifest → `verify_manifest` (parser/AST sandbox)       |
| 05 | `05_rl_training.py`               | —                | **Design only.** Gym environment + RL policy on synthetic prices (`torch` + `gymnasium` extras)    |
| 06 | `06_mcp_integration.py`           | —                | **Runnable.** Enumerate the static MCP tools from `schema/mcp/mcp_tools.json`                      |
| 07 | `07_natural_language_critique.py` | —                | **Design only.** `BacktestResult` → LLM critique → structured `Critique` report                    |
| 09 | `09_typed_llm_decision.py`        | —                | **Runnable.** Typed `LlmDecision` (veto / size-down) applied to an order intent; size increases are rejected; Journal v1 audit records |
| 10 | `10_claude_autonomous_quant.py`   | —                | **Runnable.** MCP quant agent workflow: inspect the MCP tool schema + indicator catalog, propose a mean-reversion hypothesis, backtest it, evaluate with the Deflated Sharpe Ratio; offline via `ScriptedFakeLlm` |
| 11 | `11_deterministic_ai_replay.py`   | —                | **Runnable.** Cryptographic prompt replayer: record N AI decisions to a SHA-256 prompt cache + Journal v1 NDJSON, then replay from disk with no API calls |
| 12 | `12_ai_drawdown_refinement.py`    | —                | **Runnable.** AI strategy auto-enhancer: diagnose a ≥12% drawdown streak, propose an ADX trend filter, run it through the `decision_guard` guard rules, and re-evaluate out-of-sample with DSR |

Slot 08 is intentionally unused (reserved; numbers are not reused or shifted).

## Pitfalls checklist

Every numbered script in this directory has a `Pitfalls::` section in its module docstring
(enforced by `tests/unit/test_pitfalls_sections.py`). For the four design-only scripts it lists the
traps the future code must defend against, not behaviour you can run. The recurring AI-research
traps: an LLM may already know how a historic date turned out (training-data look-ahead); output
is non-deterministic, so store the prompt, response and seed; any text pasted into a prompt or
returned by a tool is untrusted; model output is parsed by a grammar and never executed; a loop of
generated strategies is a multiple-testing problem (count every trial, keep a holdout); RL needs a
time split, costs in the reward and many seeds; and the fake backends here prove plumbing, not a
model. For the general treatment see
[Avoiding backtest biases](https://vyapaar-labs.github.io/vyapaar/book/backtesting/avoiding_backtest_biases.html).

## What actually exists in `vyapaar_examples._kernel.ai` today (offline)

| Module                                      | Symbols                                          | Runs offline? |
|---------------------------------------------|--------------------------------------------------|---------------|
| `vyapaar_examples._kernel.ai.llm.provider`   | `LlmPort`, `ScriptedFakeLlm`                     | ✅             |
| `vyapaar_examples._kernel.ai.knowledge`      | `KnowledgePack`, `build_knowledge_pack`          | ✅             |
| `vyapaar_examples._kernel.ai.ask`            | `translate_query`, `AskResult`, `build_system_prompt` | ✅             |
| `schema/mcp/mcp_tools.json`                  | MCP read-only tool catalog                       | ✅             |
| `vyapaar-agent` (gap 0002)                   | **Design only** (loop.py, hypothesis.py, evaluator.py, journal.py) | ❌ |
| `vyapaar-agent` (gap 0002)                   | **Design only** (critic.py, nl_to_strategy.py, regime_report.py) | ❌ |
| `vyapaar-agent` (gap 0002)                   | **Design only** (environment.py, agent.py, policies.py, trainer.py) | ❌ |

The CLI's `vyapaar screener ask` defaults to `ScriptedFakeLlm` — swap a real
provider (`LlmPort` impl) only when you have `openai`/`anthropic`/`litellm`
installed and an API key set.

## Running them

```bash
python examples/ai_research/01_llm_research_analyst.py --query "rsi below 30" --fake-response "rsi < 30"
python examples/ai_research/06_mcp_integration.py
python examples/ai_research/09_typed_llm_decision.py
python examples/ai_research/10_claude_autonomous_quant.py --underlying RELIANCE --seed 42
python examples/ai_research/11_deterministic_ai_replay.py --decisions 10 --seed 42
python examples/ai_research/12_ai_drawdown_refinement.py --seed 42 --out refinement.json
pytest tests/unit -q -k "llm_research or mcp_integration or typed_llm or claude_autonomous or deterministic_ai_replay or ai_drawdown"
```

## Architecture references

- `docs/gaps/0002-vyapaar-wheel-ai-provider-surface.md` — AI provider and agent loop surface gap.
- `.agents/AGENTS.md` §5.5 — NoFX idea inheritance: untrusted AI principle, closed decision grammar, cryptographic replayability.
