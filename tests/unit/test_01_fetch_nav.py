"""mutual_funds/01_fetch_nav: loading a scheme's NAV series and its latest NAV."""

from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest

from vyapaar_examples._kernel.coverage import CoverageRecord, CoverageStatus, DateInterval
from vyapaar_examples._kernel.store import ParquetBarStore
from vyapaar_examples.amfi import EXCHANGE, NavRow, nav_bars

_PATH = Path(__file__).resolve().parents[2] / "examples" / "mutual_funds" / "01_fetch_nav.py"
CODE = "120503"
NAVS = {
    dt.date(2025, 1, 2): 100.0,
    dt.date(2025, 1, 3): 101.0,
    dt.date(2025, 1, 6): 102.5,
}


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("fetch_nav", _PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed(tmp_path: Path, navs: dict[dt.date, float]) -> None:
    rows = [NavRow(CODE, "fund", nav, d) for d, nav in sorted(navs.items())]
    first, last = rows[0].date, rows[-1].date
    ParquetBarStore(tmp_path).append(
        CoverageRecord(
            exchange=EXCHANGE,
            symbol=CODE,
            timeframe="1D",
            interval=DateInterval(first, last + dt.timedelta(days=1)),
            status=CoverageStatus.FINAL,
            source="test",
            row_count=len(rows),
        ),
        nav_bars(rows),
    )


def test_run_with_scheme_returns_the_stored_nav_series(example, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("VYAAPAAR_DATA_DIR", str(tmp_path))
    _seed(tmp_path, NAVS)
    out = example.run(scheme=CODE)
    assert out["type"] == "scheme"
    assert out["scheme"] == CODE
    assert out["count"] == len(NAVS)
    assert len(out["nav_points"]) == len(NAVS)


def test_run_with_latest_returns_the_last_seeded_nav(example, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("VYAAPAAR_DATA_DIR", str(tmp_path))
    _seed(tmp_path, NAVS)
    out = example.run(scheme=CODE, latest=True)
    assert out["type"] == "latest"
    assert out["scheme"] == CODE
    assert out["nav_point"]["nav"] == 102.5
    assert out["nav_point"]["date"] == "2025-01-06"


def test_run_without_scheme_or_category_raises(example, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("VYAAPAAR_DATA_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="Provide --scheme or --category"):
        example.run()
