"""Exact-``Decimal`` quant helpers mirroring the Rust quant engines.

Small, self-contained statistics and linear-algebra routines used by the later
numbered examples (allocation, forecasting, factor regressions). They mirror
the public semantics of the Rust engines shipped in the Fincept/Quantcept
gap-closing build order — ``vyapaar-ledger-allocation``,
``vyapaar-agent-forecast``, ``vyapaar-agent-panel`` — so a learner can step
through the same math the crates run, in exact ``Decimal``, offline. The Rust
crates remain the canonical engines; these are learning-path mirrors.
"""

from __future__ import annotations

from decimal import Decimal


def returns(prices: list[Decimal]) -> list[Decimal]:
    """Simple period-over-period returns of a price series."""
    if len(prices) < 2:
        raise ValueError("returns needs at least two prices")
    return [prices[i] / prices[i - 1] - Decimal(1) for i in range(1, len(prices))]


def mean(values: list[Decimal]) -> Decimal:
    """Arithmetic mean of a non-empty sequence."""
    if not values:
        raise ValueError("mean of an empty sequence")
    return sum(values, Decimal(0)) / Decimal(len(values))


def std_dev(values: list[Decimal]) -> Decimal:
    """Population standard deviation of a non-empty sequence."""
    if not values:
        raise ValueError("std_dev of an empty sequence")
    mu = mean(values)
    variance = sum((value - mu) ** 2 for value in values) / Decimal(len(values))
    return variance.sqrt()


def covariance_matrix(panel: list[list[Decimal]]) -> list[list[Decimal]]:
    """Population covariance matrix of a row-per-observation panel.

    ``panel[p][a]`` is observation ``p`` of asset ``a``; the returned
    ``matrix[a][b]`` is the covariance of assets ``a`` and ``b``.
    """
    if not panel:
        raise ValueError("covariance_matrix of an empty panel")
    n_obs = len(panel)
    n_assets = len(panel[0])
    if any(len(row) != n_assets for row in panel):
        raise ValueError("covariance_matrix rows must have equal length")
    means = [mean([row[asset] for row in panel]) for asset in range(n_assets)]
    matrix: list[list[Decimal]] = []
    for a in range(n_assets):
        row: list[Decimal] = []
        for b in range(n_assets):
            acc = sum((obs[a] - means[a]) * (obs[b] - means[b]) for obs in panel)
            row.append(acc / Decimal(n_obs))
        matrix.append(row)
    return matrix


def solve_linear_system(matrix: list[list[Decimal]], rhs: list[Decimal]) -> list[Decimal]:
    """Solve ``matrix · x = rhs`` by Gauss-Jordan elimination.

    Partial pivoting and every arithmetic step are carried out in ``Decimal``,
    mirroring the solver inside ``vyapaar-ledger-allocation``. A singular
    matrix raises ``ArithmeticError``.
    """
    n = len(rhs)
    if n == 0:
        raise ValueError("empty linear system")
    if len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("matrix must be n x n matching the rhs length")
    m = [row[:] for row in matrix]
    b = list(rhs)
    for col in range(n):
        pivot = col
        for row in range(col + 1, n):
            if abs(m[row][col]) > abs(m[pivot][col]):
                pivot = row
        if m[pivot][col] == 0:
            raise ArithmeticError("singular matrix")
        m[col], m[pivot] = m[pivot], m[col]
        b[col], b[pivot] = b[pivot], b[col]
        pv = m[col][col]
        for x in range(col, n):
            m[col][x] /= pv
        b[col] /= pv
        pivot_row = list(m[col])
        pivot_rhs = b[col]
        for row in range(n):
            if row == col:
                continue
            factor = m[row][col]
            if factor == 0:
                continue
            for j in range(col, n):
                m[row][j] -= factor * pivot_row[j]
            b[row] -= factor * pivot_rhs
    return b


def ols(design: list[list[Decimal]], y: list[Decimal]) -> list[Decimal]:
    """Ordinary least-squares coefficients ``β = (XᵀX)⁻¹Xᵀy``.

    ``design`` rows are the regressors (include a constant column of 1s for an
    intercept) and ``y`` is the dependent variable.
    """
    n_rows = len(design)
    if n_rows == 0 or len(y) != n_rows:
        raise ValueError("design and y must have the same number of rows")
    k = len(design[0])
    if any(len(row) != k for row in design):
        raise ValueError("design rows must have equal length")
    xtx = [[Decimal(0)] * k for _ in range(k)]
    xty = [Decimal(0)] * k
    for row, yi in zip(design, y, strict=True):
        for i in range(k):
            xty[i] += row[i] * yi
            for j in range(k):
                xtx[i][j] += row[i] * row[j]
    return solve_linear_system(xtx, xty)
