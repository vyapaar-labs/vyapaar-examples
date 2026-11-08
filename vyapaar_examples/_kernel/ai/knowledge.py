# mirror: kernel-verbatim port (gap 0002: ai.knowledge surface)

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from vyapaar_examples._kernel.screener.catalog import load_catalog

__all__ = [
    "FEW_SHOT_EXAMPLES",
    "FILTER_GRAMMAR_EBNF",
    "KnowledgePack",
    "build_knowledge_pack",
]

FILTER_GRAMMAR_EBNF = """
filters    := or_expr
or_expr    := and_expr { "or" and_expr }
and_expr   := term { "and" term }
term       := "either" or_expr "end"
            | filter
filter     := metric [ "on" TIMEFRAME ] [ "for" PERIOD ] predicate
predicate  := cmp quantity
            | "between" quantity "and" quantity
            | ("in" | "not in") value { "," value }
            | ("contains" | "like") text
            | ("crosses above" | "crosses below") operand
            | ("at" | "near") preset_target
            | "within" quantity "of" preset_target
cmp        := "above" | "over" | "greater than" | "more than" | ">"
            | "at least" | "no less than" | ">="
            | "below" | "under" | "less than" | "<"
            | "at most" | "no more than" | "<="
            | "equals" | "is" | "="
            | "is not" | "not equal to" | "!="
quantity   := NUMBER [ SUFFIX ]
operand    := quantity | metric
"""

FEW_SHOT_EXAMPLES: list[dict[str, Any]] = [
    {
        "query": "market cap above 10000 Cr and rsi below 30",
        "filter_text": "market_cap_basic > 100000000000 and rsi < 30",
        "resolved_predicates": [
            {"key": "market_cap_basic", "op": "gt", "value": 100000000000.0},
            {"key": "rsi", "op": "lt", "value": 30.0},
        ],
    },
    {
        "query": "volume at least 5 Lk",
        "filter_text": "volume >= 500000",
        "resolved_predicates": [
            {"key": "volume", "op": "gte", "value": 500000.0},
        ],
    },
]


@dataclass(frozen=True)
class KnowledgePack:
    """Catalog of metrics, grammar, and presets for the ask pipeline."""

    version: str
    content_hash: str
    grammar_ebnf: str
    enums: dict[str, list[str]]
    metrics: list[dict[str, Any]]
    presets: list[dict[str, Any]]
    units: dict[str, float]
    few_shot_examples: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "content_hash": self.content_hash,
            "grammar_ebnf": self.grammar_ebnf,
            "enums": self.enums,
            "metrics": self.metrics,
            "presets": self.presets,
            "units": self.units,
            "few_shot_examples": self.few_shot_examples,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def build_knowledge_pack(version: str = "1.0.0") -> KnowledgePack:
    """Build the versioned Knowledge Pack from active single sources of truth."""
    catalog = load_catalog()

    metrics_list: list[dict[str, Any]] = []
    for m in catalog:
        metrics_list.append(
            {
                "key": m.key,
                "group": m.group,
                "value_type": m.value_type,
                "unit": m.unit,
                "aliases": list(m.aliases),
                "lookback_bars": m.lookback_bars,
                "has_timeframe": m.has_timeframe,
                "has_period": m.has_period,
            }
        )
    metrics_list.sort(key=lambda x: x["key"])

    presets_list = [
        {
            "key": "52_week_high",
            "label": "52 week high",
            "description": "Within 5% of 52-week high",
            "target_metric": "price_52_week_high",
            "aliases": ["near 52w high"],
            "lookback_bars": 252,
        },
        {
            "key": "52_week_low",
            "label": "52 week low",
            "description": "Within 5% of 52-week low",
            "target_metric": "price_52_week_low",
            "aliases": ["near 52w low"],
            "lookback_bars": 252,
        },
    ]

    all_units: dict[str, float] = {
        "%": 0.01,
        "Bn": 1_000_000_000.0,
        "Cr": 10_000_000.0,
        "Lk": 100_000.0,
        "Mn": 1_000_000.0,
        "Tn": 1_000_000_000_000.0,
    }

    enums_map = {
        "FilterOp": [
            "eq",
            "neq",
            "gt",
            "gte",
            "lt",
            "lte",
            "between",
            "in",
            "not_in",
            "like",
            "has",
            "crosses_above",
            "crosses_below",
        ],
        "Timeframe": ["1", "5", "15", "30", "60", "120", "240", "1D", "1W", "1M"],
        "MetricPeriod": ["SNAPSHOT", "TTM", "FY", "FQ", "H1", "CURRENT"],
    }

    payload_to_hash = {
        "version": version,
        "grammar": FILTER_GRAMMAR_EBNF.strip(),
        "enums": enums_map,
        "metrics": metrics_list,
        "presets": presets_list,
        "units": {k: float(v) for k, v in sorted(all_units.items())},
        "examples": FEW_SHOT_EXAMPLES,
    }
    dumped = json.dumps(payload_to_hash, sort_keys=True)
    content_hash = hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]

    return KnowledgePack(
        version=version,
        content_hash=content_hash,
        grammar_ebnf=FILTER_GRAMMAR_EBNF.strip(),
        enums=enums_map,
        metrics=metrics_list,
        presets=presets_list,
        units={k: float(v) for k, v in sorted(all_units.items())},
        few_shot_examples=FEW_SHOT_EXAMPLES,
    )
