"""Volume-weighted moving average."""
# mirror: kernel-verbatim port (gap 0006)

from __future__ import annotations

from vyapaar_examples._kernel.indicators._base import Indicator, indicator
from vyapaar_examples._kernel.indicators._rolling import RollingSum
from vyapaar_examples._kernel.indicators._util import check as _check


@indicator("vwma", "moving_average", inputs=("close", "volume"), warmup=lambda s: s.period)
class Vwma(Indicator):
    """VWMA: sum(close*volume) / sum(volume) over ``period`` bars.

    Convention: if the window's total volume is 0, returns the latest close.
    """

    def __init__(self, period: int = 20) -> None:
        self.period = _check(period)
        self._cv = RollingSum(period)
        self._vol = RollingSum(period)

    def update(self, close: float, volume: float) -> float | None:
        num = self._cv.update(close * volume)
        vol = self._vol.update(volume)
        if num is None or vol is None:
            return None
        return float(close) if vol == 0.0 else num / vol
