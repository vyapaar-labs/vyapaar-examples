"""Walk-forward optimization (WFO): rolling train/validate windows.

WFO selects parameters on a trailing training window and evaluates them on the
immediately following validation window — never overlapping, so no future
information leaks into the chosen parameters.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any

from vyapaar_examples.data import Bar


@dataclass(frozen=True, slots=True)
class WindowResult:
    """Best parameters + objective for one walk-forward window."""

    window_index: int
    params: dict[str, Any]
    train_objective: float
    validate_objective: float


def walk_forward_windows(
    bars: Sequence[Bar],
    train_size: int,
    validate_size: int,
) -> Iterator[tuple[Sequence[Bar], Sequence[Bar]]]:
    """Yield non-overlapping ``(train, validate)`` bar slices."""
    if train_size <= 0 or validate_size <= 0:
        raise ValueError("train_size and validate_size must be positive")
    index = 0
    while index + train_size + validate_size <= len(bars):
        train = bars[index : index + train_size]
        validate = bars[index + train_size : index + train_size + validate_size]
        yield train, validate
        index += validate_size


def walk_forward_optimize(
    bars: Sequence[Bar],
    param_grid: Sequence[dict[str, Any]],
    objective_fn: Callable[[Sequence[Bar], dict[str, Any]], float],
    train_size: int,
    validate_size: int,
) -> list[WindowResult]:
    """Pick the best parameter set per training window and score it on validation."""
    results: list[WindowResult] = []
    for window_index, (train, validate) in enumerate(
        walk_forward_windows(bars, train_size, validate_size)
    ):
        best_params: dict[str, Any] | None = None
        best_objective: float | None = None
        for params in param_grid:
            objective = objective_fn(train, params)
            if best_objective is None or objective > best_objective:
                best_objective = objective
                best_params = params
        assert best_params is not None and best_objective is not None
        validate_objective = objective_fn(validate, best_params)
        results.append(
            WindowResult(
                window_index=window_index,
                params=best_params,
                train_objective=best_objective,
                validate_objective=validate_objective,
            )
        )
    return results
