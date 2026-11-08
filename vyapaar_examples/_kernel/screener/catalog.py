# mirror: kernel-verbatim port (gap 0002/0003: screener catalog surface)

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

__all__ = ["Metric", "MetricCatalog", "load_catalog"]


@dataclass(frozen=True)
class Metric:
    """A metric in the screener catalog."""

    key: str
    group: str = "technical"
    value_type: str = "float"
    unit: str | None = None
    aliases: tuple[str, ...] = ()
    has_timeframe: bool = False
    has_period: bool = False
    lookback_bars: int = 1
    description: str = ""

    @property
    def name(self) -> str:
        return self.key


class MetricCatalog:
    """Catalog of available screener metrics."""

    def __init__(self, metrics: dict[str, Metric]):
        self._metrics = metrics
        self._by_type: dict[str, list[str]] = {}
        for name, metric in metrics.items():
            self._by_type.setdefault(metric.value_type, []).append(name)

    def get(self, name: str) -> Metric | None:
        return self._metrics.get(name)

    def __getitem__(self, name: str) -> Metric:
        return self._metrics[name]

    def __contains__(self, name: str) -> bool:
        return name in self._metrics

    def __iter__(self) -> Iterator[Metric]:
        return iter(self._metrics.values())

    def by_type(self, metric_type: str) -> list[str]:
        return self._by_type.get(metric_type, [])

    def all_names(self) -> list[str]:
        return list(self._metrics.keys())


def load_catalog() -> MetricCatalog:
    """Load the default metric catalog."""
    metrics_list = [
        Metric(
            "close",
            "price",
            "float",
            "INR",
            ("last", "closing price"),
            True,
            False,
            1,
            "Closing price",
        ),
        Metric(
            "open", "price", "float", "INR", ("opening price",), True, False, 1, "Opening price"
        ),
        Metric("high", "price", "float", "INR", ("high price",), True, False, 1, "High price"),
        Metric("low", "price", "float", "INR", ("low price",), True, False, 1, "Low price"),
        Metric(
            "volume",
            "volume",
            "float",
            "shares",
            ("vol", "trading volume"),
            True,
            False,
            1,
            "Trading volume",
        ),
        Metric(
            "market_cap",
            "fundamental",
            "float",
            "INR",
            ("mcap", "market capitalization"),
            False,
            False,
            1,
            "Market capitalization",
        ),
        Metric(
            "market_cap_basic",
            "fundamental",
            "float",
            "INR",
            ("market cap", "mcap"),
            False,
            False,
            1,
            "Market capitalization",
        ),
        Metric(
            "pe_ratio",
            "valuation",
            "float",
            None,
            ("pe", "price to earnings"),
            False,
            False,
            1,
            "Price-to-earnings ratio",
        ),
        Metric(
            "pb_ratio",
            "valuation",
            "float",
            None,
            ("pb", "price to book"),
            False,
            False,
            1,
            "Price-to-book ratio",
        ),
        Metric(
            "roe",
            "profitability",
            "float",
            "%",
            ("return on equity",),
            False,
            False,
            1,
            "Return on equity",
        ),
        Metric(
            "debt_equity",
            "financial_health",
            "float",
            None,
            ("debt to equity",),
            False,
            False,
            1,
            "Debt-to-equity ratio",
        ),
        Metric(
            "rsi",
            "momentum",
            "float",
            None,
            ("relative strength",),
            True,
            False,
            14,
            "Relative Strength Index",
        ),
        Metric(
            "sma20",
            "technical",
            "float",
            "INR",
            ("sma 20",),
            True,
            False,
            20,
            "20-day Simple Moving Average",
        ),
        Metric(
            "sma50",
            "technical",
            "float",
            "INR",
            ("sma 50",),
            True,
            False,
            50,
            "50-day Simple Moving Average",
        ),
    ]
    return MetricCatalog({m.key: m for m in metrics_list})
