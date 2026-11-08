"""universes/06_alpha30_equal_weight_demo: Alpha-30 specialization of the generic rebalancer."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "universes"
    / "06_alpha30_equal_weight_demo.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("ex06_demo", _PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_alpha30_equal_weight_rebalance_is_a_strategy_specialization() -> None:
    module = _load()
    strat = module.Alpha30EqualWeightRebalance()
    assert strat.name == "alpha30_equal_weight_rebalance"
    assert strat.UNIVERSE == "nifty200_alpha_30"


def test_main_prints_universe_size_and_returns_none(capsys) -> None:
    module = _load()
    assert module.main() is None
    out = capsys.readouterr().out
    assert "nifty200_alpha_30" in out
    assert "no hardcoded constituents" in out
