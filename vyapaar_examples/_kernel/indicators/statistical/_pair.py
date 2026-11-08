"""Shared helpers for paired-series statistics."""
# ruff: noqa: B905
# mirror: kernel-verbatim port (gap 0006)

from __future__ import annotations


def simple_return(prev: float, cur: float) -> float:
    """cur/prev - 1; 0.0 when prev <= 0 (undefined)."""
    return cur / prev - 1.0 if prev > 0 else 0.0


def cov_var(
    xs: list[float], ys: list[float], ddof: int
) -> tuple[float, float, float]:  # mirror accommodation (gap 0006)
    """(cov, var_x, var_y) with divisor n - ddof."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    d = n - ddof
    cxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / d
    vx = sum((x - mx) ** 2 for x in xs) / d
    vy = sum((y - my) ** 2 for y in ys) / d
    return cxy, vx, vy
