# ruff: noqa: E501
# mirror: kernel-verbatim port (gap 0002: ai.ask surface)

from __future__ import annotations

import re
from dataclasses import dataclass

from vyapaar_examples._kernel.ai.knowledge import KnowledgePack, build_knowledge_pack
from vyapaar_examples._kernel.ai.llm.provider import LlmPort
from vyapaar_examples._kernel.screener.catalog import MetricCatalog, load_catalog
from vyapaar_examples._kernel.wire.screener import (
    FilterOp,
    ScreenerFilterGroup,
    ScreenerFilterPredicate,
)

__all__ = [
    "AskResult",
    "FilterParseError",
    "QueryTranslationError",
    "build_system_prompt",
    "parse_filters",
    "translate_query",
]


@dataclass(frozen=True)
class AskResult:
    """Result of translating a natural language query to a screener filter."""

    query: str
    filter_text: str
    filter_group: ScreenerFilterGroup
    repair_count: int
    raw_responses: list[str]


class FilterParseError(ValueError):
    """Raised when parsing fails, formatted with caret positioning."""

    def __init__(self, message: str, text: str = "", position: int = 0) -> None:
        self.message = message
        self.text = text
        self.position = position
        if text:
            pos = max(0, min(position, len(text)))
            caret_line = " " * pos + "^"
            super().__init__(f"{message}\n  {text}\n  {caret_line}")
        else:
            super().__init__(message)


class QueryTranslationError(Exception):
    """Raised when the LLM output cannot be parsed or validated within repair limit."""


def build_system_prompt(knowledge: KnowledgePack) -> str:
    """Build compact system prompt containing grammar, metric keys, presets, and units."""
    sample_metrics = ", ".join(m["key"] for m in knowledge.metrics[:25])
    preset_phrases = ", ".join(p["label"] for p in knowledge.presets)
    return (
        "You are an assistant that translates natural language stock screening queries into Vyapaar filter syntax.\n"
        "Rules:\n"
        "1. Output ONLY the English filter sentence on a single line. No quotes, no markdown, no explanations.\n"
        "2. Valid comparisons: above, below, at least, at most, between X and Y, in A, B, crosses above, crosses below, near/at <preset>.\n"
        "3. Metrics include: " + sample_metrics + "...\n"
        "4. Presets include: " + preset_phrases + "\n"
        "5. Money units: Cr, Lk, Mn, Bn, Tn, %. For example: 'market cap above 5000 Cr and rsi below 30'\n"
    )


def _parse_num(val_str: str) -> float:
    s = val_str.lower().strip()
    if s.endswith("cr"):
        return float(s[:-2].strip()) * 10_000_000.0
    if s.endswith("lk"):
        return float(s[:-2].strip()) * 100_000.0
    if s.endswith("mn") or s.endswith("m"):
        suffix_len = 2 if s.endswith("mn") else 1
        return float(s[:-suffix_len].strip()) * 1_000_000.0
    if s.endswith("bn") or s.endswith("b"):
        suffix_len = 2 if s.endswith("bn") else 1
        return float(s[:-suffix_len].strip()) * 1_000_000_000.0
    if s.endswith("k"):
        return float(s[:-1].strip()) * 1_000.0
    return float(s)


def parse_filters(text: str, catalog: MetricCatalog | None = None) -> ScreenerFilterGroup:
    """Parse filter text into a ScreenerFilterGroup."""
    text = text.strip()
    if not text:
        return ScreenerFilterGroup(operator="AND", items=[])

    cat = catalog if catalog is not None else load_catalog()
    clauses = [c.strip() for c in re.split(r"\s+and\s+", text, flags=re.IGNORECASE) if c.strip()]
    if not clauses:
        return ScreenerFilterGroup(operator="AND", items=[])

    op_map: list[tuple[str, FilterOp]] = [
        (">=", FilterOp.GTE),
        ("<=", FilterOp.LTE),
        ("!=", FilterOp.NEQ),
        (">", FilterOp.GT),
        ("<", FilterOp.LT),
        ("=", FilterOp.EQ),
        ("greater than", FilterOp.GT),
        ("more than", FilterOp.GT),
        ("no less than", FilterOp.GTE),
        ("at least", FilterOp.GTE),
        ("at most", FilterOp.LTE),
        ("no more than", FilterOp.LTE),
        ("above", FilterOp.GT),
        ("below", FilterOp.LT),
        ("under", FilterOp.LT),
        ("over", FilterOp.GT),
        ("equals", FilterOp.EQ),
        ("is", FilterOp.EQ),
    ]

    predicates: list[ScreenerFilterPredicate] = []

    for clause in clauses:
        matched = False
        for op_str, op_enum in op_map:
            pattern = rf"^([a-zA-Z0-9_]+)\s+{re.escape(op_str)}\s+(.+)$"
            m = re.match(pattern, clause, flags=re.IGNORECASE)
            if m:
                key, val_str = m.group(1).lower(), m.group(2).strip()
                if key not in cat:
                    raise FilterParseError(f"Unknown metric {key!r}", text=clause)
                try:
                    val = _parse_num(val_str)
                except ValueError as exc:
                    raise FilterParseError(
                        f"Cannot parse value {val_str!r}: {exc}", text=clause
                    ) from exc
                pred = ScreenerFilterPredicate(key=key, op=op_enum, value=val)
                predicates.append(pred)
                matched = True
                break
        if not matched:
            raise FilterParseError(f"Cannot parse clause {clause!r}", text=clause)

    return ScreenerFilterGroup(operator="AND", items=predicates)


def translate_query(
    user_query: str,
    llm: LlmPort,
    catalog: MetricCatalog | None = None,
    max_repairs: int = 2,
) -> AskResult:
    """Translate natural language query into a validated ScreenerFilterGroup."""
    cat = catalog if catalog is not None else load_catalog()
    knowledge = build_knowledge_pack()
    system_prompt = build_system_prompt(knowledge)

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Translate this screener query: {user_query}"},
    ]

    repair_count = 0
    raw_responses: list[str] = []

    while repair_count <= max_repairs:
        raw_output = llm.complete(messages=messages, temperature=0.0)
        raw_responses.append(raw_output)

        filter_sentence = raw_output.strip().strip('"').strip("'")

        try:
            filter_group = parse_filters(filter_sentence, cat)
            return AskResult(
                query=user_query,
                filter_text=filter_sentence,
                filter_group=filter_group,
                repair_count=repair_count,
                raw_responses=raw_responses,
            )
        except (FilterParseError, ValueError) as err:
            repair_count += 1
            if repair_count > max_repairs:
                raise QueryTranslationError(
                    f"Failed to translate query after {max_repairs} repair attempts: {err}\n"
                    f"Last output: {filter_sentence}"
                ) from err

            messages.append({"role": "assistant", "content": filter_sentence})
            messages.append(
                {
                    "role": "user",
                    "content": f"The filter '{filter_sentence}' failed to parse: {err}. Please fix it and output ONLY the corrected filter.",
                }
            )

    raise QueryTranslationError(f"Failed to translate query after {max_repairs} repair attempts")
