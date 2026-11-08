"""Moving averages: SMA, EMA, Wilder's RMA, WMA, HMA, VWMA, DEMA, TEMA, KAMA, McGinley, ALMA, LSMA."""
# ruff: noqa: E501
# mirror: kernel-verbatim port (gap 0006)

from vyapaar_examples._kernel.indicators.moving_average.alma import Alma
from vyapaar_examples._kernel.indicators.moving_average.averages import (
    Ema,
    Rma,
    Sma,
    Wma,
    make_ma,
)
from vyapaar_examples._kernel.indicators.moving_average.dema import Dema
from vyapaar_examples._kernel.indicators.moving_average.hma import Hma
from vyapaar_examples._kernel.indicators.moving_average.kama import Kama
from vyapaar_examples._kernel.indicators.moving_average.lsma import Lsma, linreg_fit
from vyapaar_examples._kernel.indicators.moving_average.mcginley_dynamic import McGinleyDynamic
from vyapaar_examples._kernel.indicators.moving_average.tema import Tema
from vyapaar_examples._kernel.indicators.moving_average.vwma import Vwma

__all__ = [
    "Alma",
    "Dema",
    "Ema",
    "Hma",
    "Kama",
    "Lsma",
    "McGinleyDynamic",
    "Rma",
    "Sma",
    "Tema",
    "Vwma",
    "Wma",
    "linreg_fit",
    "make_ma",
]
