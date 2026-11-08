"""Static protocol surface of the engine session (custom trim, gap 0008).

The mirrored ``optimizer/algo_analytics`` engine annotates its data/result
plumbing against the harness session's protocols and lazily calls
``Vyapaar.backtest`` for real-data runs. The vyapaar runtime does not ship the
session orchestrator yet, so this module pins only the static protocol shape
the engine reads (``DataProvider.bars/.instrument``, result ``metrics`` +
``equity_curve``). The real-data orchestration path raises - loud failure by
design (D7), matching the wheel-missing state.

Owner/gap: ``vyapaar-runtime`` (Strategy Tester session) / ``vyapaar-ffi``
(wheel surface). Cited as gap ``0008-runtime-session-surface``; delete this
file together with the engine's session retargets once the wheel provides the
same session surface.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

__all__ = ["BacktestResult", "CostModel", "DataProvider", "Vyapaar"]


class DataProvider(Protocol):
    """Historical (or live) market data source (engine session protocol)."""

    def bars(
        self,
        instrument_id: Any,
        *,
        timeframe: str,
        start: Any,
        end: Any,
    ) -> Sequence[Any]:
        """Return bars in ascending time order for [start, end)."""
        ...

    def instrument(self, instrument_id: Any) -> Any:
        """Resolve symbol/exchange to full instrument metadata (tick, lot, ...)."""
        ...


class CostModel(Protocol):
    """Per-fill transaction-cost model (``apply(trade) -> Trade``)."""

    def apply(self, trade: Any) -> Any:
        """Return a cost-adjusted trade."""
        ...


class BacktestResult(Protocol):
    """Static shape the engine algorithms read off a finished backtest run."""

    strategy_name: str
    metrics: dict[str, float]
    equity_curve: list[tuple[int, float]]


class Vyapaar:
    """Session factory stub - real-data orchestration is not mirrored (gap 0008)."""

    @classmethod
    def backtest(cls, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError(
            "vyapaar does not ship the session orchestrator yet (gap "
            "0008-runtime-session-surface); the engine's real-data path needs the "
            "vyapaar-runtime Strategy Tester surface"
        )
