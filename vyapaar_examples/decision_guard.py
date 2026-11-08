"""Fail-closed, reduce-only guard around the mirrored kernel decision core for model-written
decisions (in this module below).

The core ``validate_llm_decision`` defaults a missing ``decision`` to "approve" and a missing
``decided_quantity`` to the original quantity, so an empty or malformed reply becomes an approval,
and it has no notion of protective exits. ``guard_llm_decision`` wraps it (the core is unchanged):

* A missing or invalid decision or quantity, a non-mapping reply, or any inconsistent field
  rejects the order (a VETO decision flagged ``fail_closed``) instead of approving it.
* A quantity increase is a hard error (``ValueError``, as in the core); only equal or lower
  quantities pass.
* Protective exits (stop orders, or any intent the caller marks ``reduce_only``) are never
  cancelled or shrunk by the model: a veto/size-down is ignored and flagged with a reason, and an
  unusable reply keeps the exit. A model must not leave a position larger than the strategy meant.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from vyapaar_examples._kernel.order import OrderIntent, OrderSide, OrderType

__all__ = [
    "DecisionKind",
    "GuardedDecision",
    "LlmDecision",
    "apply_llm_decision",
    "guard_llm_decision",
    "is_protective_exit",
    "validate_llm_decision",
]


_PROTECTIVE_TYPES = frozenset(
    {OrderType.STOP_MARKET, OrderType.STOP_LIMIT, OrderType.TRAILING_STOP}
)
_EPS = 1e-9


# Mirrored kernel core (honba_tamashii ai/decision.py, E5-S7) retargeted into this
# module: the vyapaar wheel ships no decision surface yet. Kernel-owner gap:
# 0006-vyapaar-wheel-kernel-domain-surface.


class DecisionKind(str, Enum):  # noqa: UP042 - kernel-verbatim port
    """The kind of decision an LLM can make on an order or intent."""

    APPROVE = "approve"
    VETO = "veto"
    SIZE_DOWN = "size_down"


@dataclass(frozen=True, slots=True)
class LlmDecision:
    """A validated, typed decision produced by an AI/LLM model.

    Safety constraints enforced by ``schema_rejects_increase``:
    - ``original_quantity`` must be positive and finite.
    - ``decided_quantity`` can NEVER exceed ``original_quantity``.
    - ``VETO`` requires ``decided_quantity == 0.0``.
    - ``APPROVE`` requires ``decided_quantity == original_quantity``.
    - ``SIZE_DOWN`` requires ``0.0 < decided_quantity < original_quantity``.
    """

    order_id: str
    symbol: str
    side: OrderSide | str
    original_quantity: float
    decision: DecisionKind
    decided_quantity: float
    rationale: str
    confidence: float | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (math.isfinite(self.original_quantity) and self.original_quantity > 0):
            raise ValueError(
                f"original_quantity must be positive and finite, got {self.original_quantity}"
            )

        if not math.isfinite(self.decided_quantity):
            raise ValueError(f"decided_quantity must be finite, got {self.decided_quantity}")

        # Hard invariant: LLM decisions cannot increase quantity
        if self.decided_quantity > self.original_quantity + 1e-9:
            raise ValueError(
                f"LLM decision cannot increase quantity: original {self.original_quantity}, "
                f"decided {self.decided_quantity} (schema_rejects_increase)"
            )

        if self.decision == DecisionKind.VETO:
            if abs(self.decided_quantity) > 1e-9:
                raise ValueError(
                    f"veto decision must have decided_quantity 0.0, got {self.decided_quantity}"
                )
        elif self.decision == DecisionKind.APPROVE:
            if abs(self.decided_quantity - self.original_quantity) > 1e-9:
                raise ValueError(
                    f"approve decision must keep original_quantity {self.original_quantity}, "
                    f"got {self.decided_quantity}"
                )
        elif self.decision == DecisionKind.SIZE_DOWN and (
            self.decided_quantity <= 1e-9 or self.decided_quantity >= self.original_quantity - 1e-9
        ):
            raise ValueError(
                f"size_down decision must have 0 < decided < original: "
                f"original {self.original_quantity}, decided {self.decided_quantity}"
            )

        if self.confidence is not None and not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    def apply_to_intent(self, intent: OrderIntent) -> OrderIntent | None:
        """Apply this decision to an OrderIntent.

        Returns:
            - ``None`` if vetoed (cancelled).
            - The original ``OrderIntent`` if approved.
            - A new ``OrderIntent`` with reduced quantity if sized down.
        """
        intent_sym = intent.instrument_id.symbol
        if self.symbol != intent_sym:
            raise ValueError(
                f"symbol mismatch: decision is for {self.symbol}, intent is for {intent_sym}"
            )

        intent_side_str = (
            intent.side.value if isinstance(intent.side, OrderSide) else str(intent.side)
        )
        decision_side_str = self.side.value if isinstance(self.side, OrderSide) else str(self.side)
        if intent_side_str.lower() != decision_side_str.lower():
            raise ValueError(
                f"side mismatch: decision is for {self.side}, intent is for {intent.side}"
            )

        if self.decision == DecisionKind.VETO:
            return None
        if self.decision == DecisionKind.APPROVE:
            return intent
        if self.decision == DecisionKind.SIZE_DOWN:
            return dataclasses.replace(intent, quantity=self.decided_quantity)
        return intent

    def to_journal_record(self) -> dict[str, Any]:
        """Convert to standard Journal v1 NDJSON audit entry."""
        return {
            "type": "llm_decision_recorded",
            "order_id": self.order_id,
            "decision": self.decision.value,
            "original_qty": self.original_quantity,
            "decided_qty": self.decided_quantity,
            "rationale": self.rationale,
            "confidence": self.confidence,
        }


def apply_llm_decision(
    intent: OrderIntent,
    decision: LlmDecision,
) -> OrderIntent | None:
    """Convenience helper to apply an LLM decision to an intent."""
    return decision.apply_to_intent(intent)


def validate_llm_decision(
    raw: dict[str, Any],
    original_intent: OrderIntent | None = None,
) -> LlmDecision:
    """Validate a raw LLM output dictionary into a typed LlmDecision.

    If ``original_intent`` is provided, fields are checked against it
    to ensure the LLM cannot flip sides, change symbols, or increase quantities.
    """
    order_id = str(raw.get("order_id", "intent-0"))
    symbol = str(raw.get("symbol", ""))
    side_raw = raw.get("side", "buy")
    decision_raw = raw.get("decision", "approve")

    if isinstance(decision_raw, DecisionKind):
        decision_kind = decision_raw
    else:
        try:
            decision_kind = DecisionKind(str(decision_raw).lower())
        except ValueError:
            raise ValueError(f"unknown decision kind {decision_raw!r}")  # noqa: B904

    orig_qty = float(raw.get("original_quantity", 0.0))
    decided_qty = float(raw.get("decided_quantity", orig_qty))
    rationale = str(raw.get("rationale", ""))
    confidence = (
        float(raw["confidence"]) if "confidence" in raw and raw["confidence"] is not None else None
    )

    if original_intent is not None:
        symbol = original_intent.instrument_id.symbol
        side_raw = original_intent.side
        orig_qty = original_intent.quantity

    return LlmDecision(
        order_id=order_id,
        symbol=symbol,
        side=side_raw,
        original_quantity=orig_qty,
        decision=decision_kind,
        decided_quantity=decided_qty,
        rationale=rationale,
        confidence=confidence,
    )


@dataclass(frozen=True, slots=True)
class GuardedDecision:
    """Outcome of ``guard_llm_decision``.

    ``effective_intent`` is what to actually submit (``None`` = cancelled). ``fail_closed`` is
    true when the reply was unusable; ``overridden`` is true when the model's decision was not
    honoured to protect an exit; ``reasons`` explains either.
    """

    decision: LlmDecision
    effective_intent: OrderIntent | None
    fail_closed: bool
    overridden: bool
    reasons: tuple[str, ...]


def is_protective_exit(intent: OrderIntent, *, reduce_only: bool = False) -> bool:
    """True for stop-type orders or when the caller flags the intent ``reduce_only``."""
    return reduce_only or intent.order_type in _PROTECTIVE_TYPES


def _is_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _kind(value: Any) -> DecisionKind | None:
    if isinstance(value, DecisionKind):
        return value
    try:
        return DecisionKind(value.lower()) if isinstance(value, str) else None
    except ValueError:
        return None


def _problem(raw: Any) -> str | None:
    """Why ``raw`` is not an explicit, well-formed decision, or None."""
    if not isinstance(raw, Mapping):
        return f"reply is not a mapping ({type(raw).__name__})"
    decision = _kind(raw.get("decision"))
    if decision is None:
        return f"missing or unknown decision {raw.get('decision')!r}"
    qty = raw.get("decided_quantity")
    if decision is DecisionKind.VETO:
        if qty is not None and not (_is_number(qty) and abs(qty) <= _EPS):
            return f"veto with non-zero decided_quantity {qty!r}"
    elif not _is_number(qty):
        return f"missing or non-numeric decided_quantity {qty!r}"
    return None


def _rejection(intent: OrderIntent, reason: str) -> LlmDecision:
    return LlmDecision(
        order_id="unparsed",
        symbol=intent.instrument_id.symbol,
        side=intent.side,
        original_quantity=intent.quantity,
        decision=DecisionKind.VETO,
        decided_quantity=0.0,
        rationale=f"fail-closed: {reason}",
    )


def guard_llm_decision(
    raw: Mapping[str, Any],
    original_intent: OrderIntent,
    *,
    reduce_only: bool = False,
) -> GuardedDecision:
    """Validate ``raw`` against ``original_intent`` and decide what may be submitted.

    Raises:
        ValueError: the model tried to increase the quantity (a hard violation, as in the core).
    """
    protective = is_protective_exit(original_intent, reduce_only=reduce_only)
    reasons: list[str] = []

    problem = _problem(raw)
    decision: LlmDecision | None = None
    if problem is None:
        explicit = dict(raw)
        if explicit.get("decided_quantity") is None and _kind(explicit["decision"]) is (
            DecisionKind.VETO
        ):
            explicit["decided_quantity"] = 0.0
        try:
            decision = validate_llm_decision(explicit, original_intent=original_intent)
        except (ValueError, TypeError) as exc:
            qty = explicit.get("decided_quantity")
            if isinstance(qty, (int, float)) and qty > original_intent.quantity + _EPS:
                raise
            problem = str(exc)
    if decision is None:
        assert problem is not None
        decision = _rejection(original_intent, problem)
        reasons.append(f"unusable model reply: {problem}")
        if protective:
            reasons.append("protective exit kept as submitted")
            return GuardedDecision(decision, original_intent, True, True, tuple(reasons))
        return GuardedDecision(decision, None, True, False, tuple(reasons))

    if protective and decision.decision is not DecisionKind.APPROVE:
        reasons.append(
            f"{decision.decision.value} ignored: protective exit "
            "(stop order or reduce_only) must not be cancelled or shrunk"
        )
        return GuardedDecision(decision, original_intent, False, True, tuple(reasons))

    effective = (
        None
        if decision.decision is DecisionKind.VETO
        else dataclasses.replace(original_intent, quantity=decision.decided_quantity)
    )
    return GuardedDecision(decision, effective, False, False, tuple(reasons))
