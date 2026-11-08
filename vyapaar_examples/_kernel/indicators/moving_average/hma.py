"""Hull moving average."""
# mirror: kernel-verbatim port (gap 0006)

from __future__ import annotations

import math

from vyapaar_examples._kernel.indicators._base import Indicator, indicator
from vyapaar_examples._kernel.indicators._util import check as _check
from vyapaar_examples._kernel.indicators.moving_average.averages import Wma


@indicator("hma", "moving_average", warmup=lambda s: s.period + s._root - 1)
class Hma(Indicator):
    """Hull MA: WMA(2*WMA(x, n//2) - WMA(x, n), floor(sqrt(n))) (TradingView ta.hma)."""

    def __init__(self, period: int = 9) -> None:
        self.period = _check(period)
        self._root = max(1, int(math.sqrt(period)))
        self._half = Wma(max(1, period // 2))
        self._full = Wma(period)
        self._out = Wma(self._root)

    def update(self, x: float) -> float | None:
        h, f = self._half.update(x), self._full.update(x)
        if h is None or f is None:
            return None
        return self._out.update(2.0 * h - f)
