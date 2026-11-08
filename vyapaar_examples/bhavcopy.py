"""vyapaar_examples.bhavcopy: parse NSE EOD bhavcopy CSVs into Bars, dialect-sniffed.

NSE has published its end-of-day bhavcopy under three header dialects over the years: the
current UDiFF format (``TradDt``/``TckrSymb``/``SctySrs``), the Sec Bhavdata format
(``DATE1``/``SYMBOL``/``SERIES``/``OPEN_PRICE``) and the legacy format
(``TIMESTAMP``/``SYMBOL``/``SERIES``/``OPEN``). Vyapaar's own loader surface for this is
absent - gap 0003 - so this module is where the bhavcopy dialect-sniffing format is written
down and tested.

Only the ``EQ``, ``BE`` and ``BZ`` series survive; every other series is dropped before the
row is read. ``high`` is clamped up to at least ``max(open, close)``, ``low`` down to
``min(open, close)`` and a negative volume to ``0`` - the invariants
``ParquetBarStore.append`` validates, so an anomalous exchange row still stores. A missing or
unparseable date falls back to the wall clock's current IST date. An unrecognised header is
not an error: parsing returns an empty dict instead of raising.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
from dataclasses import dataclass

from vyapaar_examples._kernel.bar import Bar
from vyapaar_examples._kernel.instrument import InstrumentId
from vyapaar_examples.synthetic import session_ts

__all__ = ["parse_bhavcopy_csv"]

_IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
_SERIES_KEPT = frozenset({"EQ", "BE", "BZ"})


@dataclass(frozen=True)
class _Dialect:
    """One recognised bhavcopy header shape, keyed by its upper-cased field names."""

    required: frozenset[str]
    date_format: str
    date_key: str
    symbol_key: str
    series_key: str
    ohlcv_keys: tuple[str, str, str, str, str]  # open, high, low, close, volume


_DIALECTS: tuple[_Dialect, ...] = (
    _Dialect(
        required=frozenset({"TRADDT", "TCKRSYMB", "SCTYSRS"}),
        date_format="%Y-%m-%d",
        date_key="TRADDT",
        symbol_key="TCKRSYMB",
        series_key="SCTYSRS",
        ohlcv_keys=("OPNPRIC", "HGHPRIC", "LWPRIC", "CLSPRIC", "TTLTRADQTY"),
    ),
    _Dialect(
        required=frozenset({"DATE1", "SYMBOL", "SERIES", "OPEN_PRICE"}),
        date_format="%d-%m-%Y",
        date_key="DATE1",
        symbol_key="SYMBOL",
        series_key="SERIES",
        ohlcv_keys=("OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "CLOSE_PRICE", "TTL_TRD_QNTY"),
    ),
    _Dialect(
        required=frozenset({"TIMESTAMP", "SYMBOL", "SERIES", "OPEN"}),
        date_format="%d-%m-%Y",
        date_key="TIMESTAMP",
        symbol_key="SYMBOL",
        series_key="SERIES",
        ohlcv_keys=("OPEN", "HIGH", "LOW", "CLOSE", "TOTTRDQTY"),
    ),
)


def parse_bhavcopy_csv(csv_content: str, exchange: str = "NSE") -> dict[str, Bar]:
    """Bars keyed by symbol, dialect-sniffed from ``csv_content``'s header.

    See the module docstring for the three dialects recognised. Rows outside the
    ``EQ``/``BE``/``BZ`` series are dropped; the last row for a repeated symbol wins. An
    unrecognised header returns an empty dict rather than raising.
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    field_map = {name.strip().upper(): name for name in reader.fieldnames or [] if name}
    upper_fields = set(field_map)

    dialect = next((d for d in _DIALECTS if d.required <= upper_fields), None)
    if dialect is None:
        return {}

    date_col = field_map[dialect.date_key]
    symbol_col = field_map[dialect.symbol_key]
    series_col = field_map[dialect.series_key]
    open_col, high_col, low_col, close_col, volume_col = (
        field_map[key] for key in dialect.ohlcv_keys
    )

    bars: dict[str, Bar] = {}
    for row in reader:
        series = (row.get(series_col) or "").strip().upper()
        if series not in _SERIES_KEPT:
            continue
        symbol = (row.get(symbol_col) or "").strip()
        day = _parse_date(row.get(date_col) or "", dialect.date_format)
        open_ = float(row[open_col])
        high = float(row[high_col])
        low = float(row[low_col])
        close = float(row[close_col])
        volume = float(row[volume_col])
        bars[symbol] = Bar(
            instrument_id=InstrumentId(symbol, exchange),
            ts=session_ts(day),
            open=open_,
            high=max(high, open_, close),
            low=min(low, open_, close),
            close=close,
            volume=max(volume, 0.0),
        )
    return bars


def _parse_date(text: str, date_format: str) -> dt.date:
    """``text`` as a calendar date in ``date_format``, or today's IST date when that fails."""
    try:
        return dt.datetime.strptime(text, date_format).date()
    except ValueError:
        return dt.datetime.now(tz=_IST).date()
