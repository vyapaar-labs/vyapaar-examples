"""01 — Loading data.

Loads a synthetic price series, reports coverage and the latest close, and
writes/reads it through a Polars-backed CSV so the pipeline is fully offline.

Pitfalls::
    - Look-ahead bias: never let a bar's information leak into a decision made
      *before* that bar's close. Backtests must step bar-by-bar and only use
      data already seen.
    - T+1 settlement: Indian equities settle T+1; intraday volume may not be
      cash-settled the same day. Position reports are end-of-day snapshots.
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path
from typing import Any

from vyapaar_examples import SampleInstruments, synthetic_bars


def _write_bars_csv(bars: list[Any], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["instrument", "ts", "open", "high", "low", "close", "volume"])
        for bar in bars:
            writer.writerow(
                [
                    bar.instrument,
                    bar.ts.isoformat(),
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    bar.volume,
                ]
            )


def _read_bars_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main() -> dict[str, object]:
    instrument = SampleInstruments.NIFTY50
    bars = synthetic_bars(instrument, days=250, seed=42)
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = Path(tmp) / "bars.csv"
        _write_bars_csv(bars, csv_path)
        rows = _read_bars_csv(csv_path)

    return {
        "instrument": instrument.value,
        "bars_generated": len(bars),
        "rows_reloaded": len(rows),
        "first_ts": bars[0].ts.isoformat(),
        "last_close": str(bars[-1].close),
        "monotonic_ts": all(bars[i].ts < bars[i + 1].ts for i in range(len(bars) - 1)),
    }


if __name__ == "__main__":
    print(main())
