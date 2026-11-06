"""10_walkforward_optimization regression test."""

from __future__ import annotations


def test_example_10_runs_walk_forward_windows(load_example) -> None:
    module = load_example("10_walkforward_optimization")
    result = module.main()
    # 240 bars: train=120, validate=40 -> windows at 0, 40, 80 => 3 windows.
    assert result["windows"] == 3
    assert len(result["chosen_params"]) == 3
    assert all(set(window) == {"lookback"} for window in result["chosen_params"])
    # Objectives are finite floats.
    for objectives in (result["train_objectives"], result["validate_objectives"]):
        assert len(objectives) == 3
        assert all(isinstance(value, float) for value in objectives)
