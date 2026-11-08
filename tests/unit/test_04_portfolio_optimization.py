"""mutual_funds/04_portfolio_optimization: mean-variance optimization over NAV series."""

from __future__ import annotations

import datetime as dt
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("numpy")
pytest.importorskip("scipy")

from vyapaar_examples._kernel.coverage import CoverageRecord, CoverageStatus, DateInterval
from vyapaar_examples._kernel.store import ParquetBarStore
from vyapaar_examples.amfi import EXCHANGE, NavRow, nav_bars

_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "mutual_funds"
    / "04_portfolio_optimization.py"
)


@pytest.fixture(scope="module")
def example():
    spec = importlib.util.spec_from_file_location("portfolio_optimization", _PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _seed(tmp_path: Path, scheme: str, navs: dict[dt.date, float]) -> None:
    rows = [NavRow(scheme, "fund", nav, d) for d, nav in sorted(navs.items())]
    first, last = rows[0].date, rows[-1].date
    ParquetBarStore(tmp_path).append(
        CoverageRecord(
            exchange=EXCHANGE,
            symbol=scheme,
            timeframe="1D",
            interval=DateInterval(first, last + dt.timedelta(days=1)),
            status=CoverageStatus.FINAL,
            source="test",
            row_count=len(rows),
        ),
        nav_bars(rows),
    )


def test_optimal_weights_sum_to_one_and_respect_bounds(example, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("VYAAPAAR_DATA_DIR", str(tmp_path))
    start = dt.date(2024, 1, 1)
    days = [start + dt.timedelta(days=i) for i in range(60)]
    _seed(tmp_path, "AAA", {d: 100.0 * (1.01**i) for i, d in enumerate(days)})
    _seed(tmp_path, "BBB", {d: 100.0 * (1.002**i) for i, d in enumerate(days)})
    _seed(tmp_path, "CCC", {d: 100.0 * (0.999**i) for i, d in enumerate(days)})
    out = example.run(
        schemes=["AAA", "BBB", "CCC"],
        start=start,
        end=days[-1],
        max_weight=0.6,
        min_weight=0.05,
    )
    weights = out["optimal_weights"]
    assert set(weights) == {"AAA", "BBB", "CCC"}
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-4)
    for w in weights.values():
        assert 0.05 - 1e-6 <= w <= 0.6 + 1e-6
    assert "sharpe" in out["portfolio"]
    assert isinstance(out["optimization_success"], bool)


def test_fewer_than_two_schemes_raises(example, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("VYAAPAAR_DATA_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="at least 2 schemes"):
        example.run(schemes=["AAA"], start=dt.date(2024, 1, 1), end=dt.date(2024, 2, 1))
