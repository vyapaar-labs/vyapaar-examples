"""Backward compatibility re-exports for vyapaar.entities.

Entities are split into:
- vyapaar.domain: Pure domain models (Bar, Instrument, Order, Position, Portfolio, etc.)
- vyapaar.wire: Serialization and wire contracts (ADR 006)
"""
# ruff: noqa: F822

from typing import Any

from vyapaar_examples._kernel import (
    AggressorSide,
    Bar,
    Instrument,
    InstrumentId,
    InstrumentKind,
    Money,
    OrderIntent,
    OrderSide,
    OrderStatus,
    OrderType,
    Portfolio,
    Position,
    QuoteTick,
    TimeInForce,
    Trade,
    TradeTick,
)
from vyapaar_examples._kernel import bar as bar
from vyapaar_examples._kernel import instrument as instrument
from vyapaar_examples._kernel import order as order
from vyapaar_examples._kernel import portfolio as portfolio
from vyapaar_examples._kernel import position as position
from vyapaar_examples._kernel import tick as tick
from vyapaar_examples._kernel import trade as trade
from vyapaar_examples._kernel.wire import (
    ENUMS,
    MODELS,
    BarAggregation,
    BarEvent,
    BarSpecification,
    Currency,
    Event,
    FilterOp,
    Message,
    MetricDefinition,
    MetricKeySpec,
    MetricPeriod,
    MetricRef,
    Order,
    OrderAccepted,
    OrderCancelled,
    OrderCancelRequested,
    OrderEvent,
    OrderExpired,
    OrderFilled,
    OrderPartiallyFilled,
    OrderRejected,
    PositionSide,
    PriceType,
    QuoteEvent,
    ScreenerFilterGroup,
    ScreenerFilterPredicate,
    ScreenerRow,
    ScreenerScanRequest,
    ScreenerScanResponse,
    ScreenerSortSpec,
    Str,
    Timeframe,
    TradeEvent,
    UnitType,
    UnixNanos,
    ValueType,
    WireOrderSide,
    WireOrderType,
    WireTimeInForce,
    loads,
    loads_many,
)
from vyapaar_examples._kernel.wire import base as _wire_base
from vyapaar_examples._kernel.wire import screener as screener
from vyapaar_examples._kernel.wire import wire as wire

__all__ = [
    "ENUMS",
    "MODELS",
    "SCHEMA_VERSION",
    "AggressorSide",
    "Bar",
    "BarAggregation",
    "BarEvent",
    "BarSpecification",
    "Currency",
    "Event",
    "FilterOp",
    "Instrument",
    "InstrumentId",
    "InstrumentKind",
    "Message",
    "MetricDefinition",
    "MetricKeySpec",
    "MetricPeriod",
    "MetricRef",
    "Money",
    "Order",
    "OrderAccepted",
    "OrderCancelRequested",
    "OrderCancelled",
    "OrderEvent",
    "OrderExpired",
    "OrderFilled",
    "OrderIntent",
    "OrderPartiallyFilled",
    "OrderRejected",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Portfolio",
    "Position",
    "PositionSide",
    "PriceType",
    "QuoteEvent",
    "QuoteTick",
    "ScreenerFilterGroup",
    "ScreenerFilterPredicate",
    "ScreenerRow",
    "ScreenerScanRequest",
    "ScreenerScanResponse",
    "ScreenerSortSpec",
    "Str",
    "TimeInForce",
    "Timeframe",
    "Trade",
    "TradeEvent",
    "TradeTick",
    "UnitType",
    "UnixNanos",
    "ValueType",
    "WireOrderSide",
    "WireOrderType",
    "WireTimeInForce",
    "_wire_base",
    "bar",
    "instrument",
    "loads",
    "loads_many",
    "order",
    "portfolio",
    "position",
    "screener",
    "tick",
    "trade",
    "wire",
]


def __getattr__(name: str) -> Any:
    """Lazy native-backed constants (SCHEMA_VERSION): they need the compiled extension."""
    if name in {"SCHEMA_VERSION"}:
        return getattr(wire, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
